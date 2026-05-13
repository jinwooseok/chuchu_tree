# 스터디 기능 - 백엔드 도메인 & API 설계 문서

---

## 구현 현황 (2026-03-03 기준)

### 완료된 항목

| 분류 | 항목 |
|------|------|
| 기반 구조 | study 도메인 전체 아키텍처 (domain/application/infra/presentation) |
| UserCode | `user_account.user_code` VARCHAR(6) 컬럼 추가, 신규 가입 시 자동 생성 |
| 스터디 CRUD | 생성, 조회(비인증 허용), 수정, 삭제, 이름 검증, 검색 |
| 멤버 관리 | 탈퇴(방장 위임 포함), 강제 퇴장, 내 스터디 목록(`ownerUserCode` 포함) |
| 초대 | 발송(Notice+SSE), 취소, 수락(Notice 발송), 거절(Notice 발송) |
| 초대 목록 | 내 초대 목록(`inviterUserCode` 포함), 스터디 내 초대 목록(멤버 권한) |
| 신청 | 신청(Notice+SSE to owner), 취소, 목록 조회(멤버 권한), 수락/거절(Notice 발송) |
| 문제 할당 | 전원 할당(`/all`), 개인별 할당(멤버·날짜 독립), 삭제, 날짜별 조회 |
| 문제 조회 | 날짜별 그룹 + 멤버 풀이 현황(`solveInfo`) 포함 |
| 문제 추천 | `GET /studies/{id}/recommend-problems` (멤버 풀이 현황 + all_unsolved 필터) |
| 알림 | 조회(카테고리별 JSON content dict), 일괄 읽음, SSE 스트림 |
| study_problem 정규화 | `study_problem_member` 테이블 분리, 날짜별 개인 독립 할당 |
| /bj-accounts/me | `studies` 목록 + `userCode` 포함 |
| 회원탈퇴 | study_problem_member hard delete, study_member soft delete + 방장 위임 |

### 미완료 항목 (다음 PR 예정)

| 항목 | 비고 |
|------|------|
| SSE Manager multi-process 지원 | 현재 in-memory asyncio.Queue — 멀티 워커 환경 미지원. Redis pub/sub 전환 필요 |
| USER_PROBLEMS_STATUS 알림 | 문제 풀이 완료 시 알림 발송 (타 도메인 연동) |
| USER_TIER_STATUS 알림 | 티어 변경 시 알림 발송 (타 도메인 연동) |
| STUDY_PROBLEMS_STATUS 알림 | 문제 할당 시 대상 멤버별 알림 발송 (현재 미발송) |

---

## 구현 목표
친구들과 함께 백준 문제를 풀고 싶은 요구사항을 충족하는 스터디(Study) 기능을 추가한다.
기존 chuchu_tree 백엔드의 Clean Architecture 패턴(domain/application/infra/presentation)과
DI, Repository, CQRS, @transactional 패턴을 그대로 따른다.

## 전역 제약: 백준 계정 연동 필수

> **스터디의 모든 참여 행위(생성, 초대 수락, 가입신청)는 백준 계정이 현재 연동된 유저만 가능하다.**
> 풀이 여부 판단, 멤버 통계 등 모든 문제 관련 로직은 연동된 계정 기준으로 처리한다.

- 백준 계정 미연동 유저가 참여를 시도하면 `BJ_ACCOUNT_NOT_LINKED (400)` 반환
- 초대 발송 시 피초대자의 연동 여부도 서비스 레이어에서 검증
- 가입신청 수락 시에도 신청자의 연동 여부 재검증
- 풀문제 전체 할당(`/problems/all`) 시 `target_user_account_ids`에는 **연동된 멤버만** 포함

---

## 0. 사전 작업: UserCode 추가

### 배경
사용자 식별을 위해 `{bjAccountId}#{userCode}` 형식이 필요하다.
현재 `user_account` 테이블에는 `user_code` 필드가 없으므로 추가해야 한다.

### 변경 파일
- `app/user/infra/model/user_account.py`
- `app/user/domain/entity/user_account.py`
- `app/user/infra/mapper/user_account_mapper.py`
- `app/user/infra/repository/user_account_repository_impl.py`
- `alembic/versions/` (신규 migration)

### 스펙
```
컬럼: user_code VARCHAR(6) NULL → NOT NULL (마이그레이션 후 backfill)
      UNIQUE 제약 + Index('idx_user_code', 'user_code')
값:   "000000" ~ "999999" (6자리 zero-padded 10진수)
생성: UserAccountRepositoryImpl.insert() 내부에서
      - 랜덤 6자리 생성 → DB 중복 체크 → 최대 100회 재시도
      - 고갈 시 APIException(ErrorCode.USER_CODE_EXHAUSTED)
```

---

## 1. 신규 Value Objects
> `app/common/domain/vo/identifiers.py` 에 추가

```python
StudyId, StudyMemberId, StudyInvitationId,
StudyApplicationId, StudyProblemId, NoticeId
```

---

## 2. 신규 Enum
> `app/common/domain/enums.py` 에 추가

| Enum | 값 |
|------|----|
| `StudyMemberRole` | OWNER, MEMBER |
| `InvitationStatus` | PENDING, ACCEPTED, REJECTED |
| `ApplicationStatus` | PENDING, ACCEPTED, REJECTED |
| `NoticeCategory` | STUDY_INVITATION_STATUS, STUDY_APPLICATION_STATUS, STUDY_PROBLEMS_STATUS, USER_PROBLEMS_STATUS, USER_TIER_STATUS, SYSTEM_ANNOUNCEMENT |

> `CalendarProblemScope` 없음. 할당 범위(전체/부분)는 `target_user_account_ids`의 내용으로 서비스 레이어에서 결정.

---

## 3. 도메인 엔티티 설계

### 3.1 Study (Aggregate Root)
> `app/study/domain/entity/study.py`
> 테이블: `study`

| 필드 | 타입 | 설명 |
|------|------|------|
| study_id | StudyId \| None | PK |
| study_name | str | 스터디명 (UNIQUE) |
| owner_user_account_id | UserAccountId | 방장 |
| description | str \| None | 설명 (max 200) |
| max_members | int | 최대 인원 (default 10) |
| created_at, updated_at, deleted_at | datetime | 타임스탬프 |
| members | list[StudyMember] | 멤버 목록 (eager load) |

**도메인 메서드**: `create()`, `add_member()`, `remove_member()`, `is_member()`, `is_owner()`, `is_full()`

**테이블 제약**: `UniqueConstraint('study_name')`, `Index('idx_study_owner', 'owner_user_account_id')`

---

### 3.2 StudyMember (Child Entity of Study)
> `app/study/domain/entity/study_member.py`
> 테이블: `study_member`

| 필드 | 타입 |
|------|------|
| study_member_id | StudyMemberId \| None |
| study_id | StudyId |
| user_account_id | UserAccountId |
| role | StudyMemberRole |
| joined_at | datetime |
| created_at, updated_at, deleted_at | datetime |

**테이블 제약**: `UniqueConstraint('study_id', 'user_account_id')`, 복합 Index

---

### 3.3 StudyInvitation (Aggregate Root)
> `app/study/domain/entity/study_invitation.py`
> 테이블: `study_invitation`

| 필드 | 타입 | 설명 |
|------|------|------|
| invitation_id | StudyInvitationId \| None | |
| study_id | StudyId | |
| invitee_user_account_id | UserAccountId | 초대 받는 사람 |
| inviter_user_account_id | UserAccountId | 초대 하는 사람 (방장) |
| status | InvitationStatus | PENDING / ACCEPTED / REJECTED |
| responded_at | datetime \| None | |
| created_at, updated_at, deleted_at | datetime | |

**도메인 메서드**: `create()`, `accept()`, `reject()`

**테이블 제약**: `UniqueConstraint('study_id', 'invitee_user_account_id')` (PENDING만 1개 허용)

---

### 3.4 StudyApplication (Aggregate Root)
> `app/study/domain/entity/study_application.py`
> 테이블: `study_application`

| 필드 | 타입 | 설명 |
|------|------|------|
| application_id | StudyApplicationId \| None | |
| study_id | StudyId | |
| applicant_user_account_id | UserAccountId | 신청자 |
| status | ApplicationStatus | |
| message | str \| None | 가입 메시지 (max 300) |
| responded_at | datetime \| None | |
| created_at, updated_at, deleted_at | datetime | |

**도메인 메서드**: `create()`, `accept()`, `reject()`

---

### 3.5 StudyProblem (Aggregate Root)
> `app/study/domain/entity/study_problem.py`
> 테이블: `study_problem`

| 필드 | 타입 | 설명 |
|------|------|------|
| study_problem_id | StudyProblemId \| None | PK |
| study_id | StudyId | |
| problem_id | ProblemId | |
| assigned_by_user_account_id | UserAccountId | 등록한 사람 |
| created_at, updated_at, deleted_at | datetime | |

> **[정규화 완료]** 기존 `target_user_account_ids` JSON 컬럼과 `target_date`는 `study_problem_member` 테이블로 분리되었습니다.
> 멤버별·날짜별 독립 할당이 가능합니다.

### 3.5.1 StudyProblemMember (Child Entity of StudyProblem)
> `app/study/infra/model/study_problem_member.py`
> 테이블: `study_problem_member`

| 필드 | 타입 | 설명 |
|------|------|------|
| study_problem_member_id | StudyProblemMemberId \| None | PK |
| study_problem_id | StudyProblemId | FK → study_problem |
| user_account_id | UserAccountId | 할당된 멤버 |
| target_date | date | 해당 멤버의 풀어야 하는 날짜 |

**할당 범위 처리 (서비스 레이어)**
- 전체 할당(`/all`): 스터디 멤버 전원에 동일 날짜로 `study_problem_member` 레코드 생성
- 개인별 할당: 요청의 `assignments` 배열(멤버·날짜)마다 개별 레코드 생성 — 멤버마다 날짜 독립 지정 가능

**도메인 메서드**: `create()`

**테이블 스펙**:
- `Index('idx_spm_study_problem', 'study_problem_id')`
- `Index('idx_spm_user_date', 'user_account_id', 'target_date')`

---

### 3.6 Notice (Aggregate Root)
> `app/study/domain/entity/notice.py`
> 테이블: `notice`

| 필드 | 타입 | 설명 |
|------|------|------|
| notice_id | NoticeId \| None | |
| recipient_user_account_id | UserAccountId | 수신자 |
| category | NoticeCategory | |
| title | str | |
| content | dict | 카테고리별 JSON 구조 (아래 참조) |
| is_read | bool | default False |
| reference_id | int \| None | 연관 엔티티 ID |
| reference_type | str \| None | 'STUDY', 'INVITATION' 등 |
| created_at, updated_at, deleted_at | datetime | |

**content 구조 (카테고리별)**:
- `STUDY_INVITATION_STATUS`: `{"studyName": str, "userId": str, "userCode": str, "status": str}`
- `STUDY_APPLICATION_STATUS`: `{"studyName": str, "status": str}`

**도메인 메서드**: `create()`, `mark_as_read()`

**테이블 인덱스**: `(recipient_user_account_id, is_read, created_at)`

---

## 4. Repository 인터페이스 (ABC)
> `app/study/domain/repository/`

| Repository | 주요 메서드 |
|------------|-----------|
| `StudyRepository` | insert, find_by_id, find_by_name, search(keyword, limit=5), update, soft_delete, is_name_taken |
| `StudyInvitationRepository` | insert, find_by_id, find_pending_by_invitee, find_by_study_and_invitee, find_pending_by_study, update |
| `StudyApplicationRepository` | insert, find_by_id, find_pending_by_study, find_by_study_and_applicant, update |
| `StudyProblemRepository` | insert, find_by_id, find_by_study_and_date_range, find_by_user_and_date_range, soft_delete |
| `StudyProblemMemberRepository` | insert_many, find_by_study_problem_id, delete_by_user_account_id (회원탈퇴 시 hard delete) |
| `NoticeRepository` | insert, insert_many, find_by_recipient, find_unread_count_by_recipient, update, mark_by_ids |
| `UserSearchRepository` (read-only DTO) | search_by_keyword(keyword, limit=5), find_by_user_account_id |

> `UserSearchResult`: `@dataclass(frozen=True)` DTO (user_account_id, bj_account_id, user_code)
> `user_account` INNER JOIN `account_link` INNER JOIN `bj_account` 쿼리 — INNER JOIN이므로 연동된 유저만 결과에 포함됨 (도메인 경계 교차 허용, read-only)

`StudyProblemRepository.find_by_user_and_date_range`: `target_user_account_ids` JSON 컬럼에 특정 user_account_id가 포함된 레코드를 조회 (MySQL JSON_CONTAINS 또는 JSON_OVERLAPS 활용)

---

## 5. API 엔드포인트

> 모두 `/api/v1` prefix. 인증: `current_user: CurrentUser = Depends(get_current_member)`

### 5.1 유저 검색
| Method | URL | 권한 | 설명 |
|--------|-----|------|------|
| GET | `/user-accounts/search?keyword=` | 인증 | bjAccountId 또는 userCode로 최대 5명 검색 |

**검색 대상**: 백준 계정이 현재 연동된 유저만 반환 (`user_account` + `account_link` + `bj_account` JOIN).
연동이 없는 유저는 검색 결과에 포함되지 않는다.

**검색 조건** (OR):
- `bj_account.bj_account_id` LIKE `%keyword%`
- `user_account.user_code` LIKE `%keyword%`

**응답**: `{ users: [{bjAccountId, userCode}] }`
식별자 표시 형식: `{bjAccountId}#{userCode}` (예: `startlink#000000`)

---

### 5.2 스터디 이름 중복 검증
| Method | URL | 권한 | 설명 |
|--------|-----|------|------|
| GET | `/studies/validate-name?name=` | 인증 | 스터디명 중복 확인 |

**응답**: `{ isAvailable: boolean }`

---

### 5.3 스터디 CRUD
| Method | URL | 권한 | 설명 |
|--------|-----|------|------|
| POST | `/studies` | 인증 | 스터디 생성 + 초대 발송 |
| GET | `/studies/{study_id}` | **없음 (비인증 허용)** | 스터디 상세 조회 — 토큰 없이도 조회 가능 |
| PATCH | `/studies/{study_id}` | 방장 | 설명/최대인원 수정 |
| DELETE | `/studies/{study_id}` | 방장 | 스터디 삭제 (soft delete) |

**POST /studies 요청**:
```json
{
  "studyName": "string (max 50)",
  "description": "string | null",
  "maxMembers": 10,
  "inviteeUserAccountIds": [1, 2, 3]
}
```
**검증**: 요청자(방장) 본인의 백준 계정 연동 필수. 초대 대상자(inviteeUserAccountIds)도 연동된 유저만 허용 (`BJ_ACCOUNT_NOT_LINKED`).

**스터디 검색**:
| Method | URL | 권한 | 설명 |
|--------|-----|------|------|
| GET | `/studies/search?keyword=` | 인증 | 스터디명/방장 bjId/방장 userCode로 최대 5개 검색 |

**응답**: `{ studies: [{studyId, studyName, ownerBjAccountId, ownerUserCode, memberCount}] }`

**내 스터디 목록**:
| Method | URL | 권한 | 설명 |
|--------|-----|------|------|
| GET | `/user-accounts/me/studies` | 인증 | 내가 속한 스터디 목록 |

---

### 5.4 스터디 멤버 관리
| Method | URL | 권한 | 설명 |
|--------|-----|------|------|
| POST | `/studies/{study_id}/members/leave` | 멤버(방장 불가) | 스터디 탈퇴 |
| DELETE | `/studies/{study_id}/members/{member_user_account_id}` | 방장 | 멤버 강퇴 |

---

### 5.5 초대 (Invitation) 흐름
| Method | URL | 권한 | 설명 |
|--------|-----|------|------|
| GET | `/studies/{study_id}/invitations` | **멤버** | 스터디 내 발송된 초대 목록 — 방장뿐 아니라 멤버 전체 조회 가능 |
| POST | `/studies/{study_id}/invitations` | 방장 | 초대 발송 (body: `{inviteeUserAccountId}`) |
| DELETE | `/studies/{study_id}/invitations/{invitation_id}` | 방장 | 초대 취소 |
| GET | `/user-accounts/me/invitations` | 인증 | 내가 받은 초대 목록 (`inviterUserCode` 포함) |
| POST | `/user-accounts/me/invitations/{invitation_id}/accept` | 초대받은 본인 | 초대 수락 |
| POST | `/user-accounts/me/invitations/{invitation_id}/reject` | 초대받은 본인 | 초대 거절 |

**초대 발송 시**: 피초대자의 백준 계정 연동 여부 검증 (`BJ_ACCOUNT_NOT_LINKED`)
**초대 수락 시**: 수락자의 백준 계정 연동 여부 재검증 → invitation.accept() → study.add_member() → Notice 발송 (방장에게)

---

### 5.6 가입신청 (Application) 흐름
| Method | URL | 권한 | 설명 |
|--------|-----|------|------|
| POST | `/studies/{study_id}/applications` | 인증(비멤버, 백준 연동 필수) | 가입 신청 (body: `{message?}`) |
| DELETE | `/studies/{study_id}/applications/me` | 신청자 본인 | 가입 신청 취소 |
| GET | `/studies/{study_id}/applications` | **멤버** | 가입신청 목록 조회 — 방장뿐 아니라 멤버 전체 조회 가능 |
| POST | `/studies/applications/{application_id}/accept` | 방장 | 가입신청 수락 |
| POST | `/studies/applications/{application_id}/reject` | 방장 | 가입신청 거절 |

---

### 5.7 스터디 풀문제 관리
| Method | URL | 권한 | 설명 |
|--------|-----|------|------|
| POST | `/studies/{study_id}/problems/all` | 방장 | 전체 멤버에게 문제 할당 |
| POST | `/studies/{study_id}/problems` | 방장 | 특정 멤버(들)에게 문제 할당 |
| DELETE | `/studies/{study_id}/problems/{study_problem_id}` | 방장 | 풀문제 삭제 |

**전체 멤버 할당 요청** (`POST /studies/{study_id}/problems/all`):
```json
{
  "problemId": 1234,
  "targetDate": "2026-03-15"
}
```
서비스 레이어에서 스터디 멤버 전원에게 동일 날짜로 `study_problem_member` 레코드 생성.
(미구현) 해당 멤버들에게 `STUDY_PROBLEMS_STATUS` Notice 일괄 발송 예정

**개인별 할당 요청** (`POST /studies/{study_id}/problems`):
```json
{
  "problemId": 1234,
  "assignments": [
    {"userAccountId": 1, "targetDate": "2026-03-15"},
    {"userAccountId": 2, "targetDate": "2026-03-16"}
  ]
}
```
멤버마다 독립적인 날짜를 지정하여 할당. `study_problem_member` 레코드를 `assignments` 배열만큼 개별 생성.
(미구현) 각 멤버에게 `STUDY_PROBLEMS_STATUS` Notice 발송 예정.

---

### 5.8 스터디 풀문제 조회 (월별)
| Method | URL | 권한 | 설명 |
|--------|-----|------|------|
| GET | `/studies/{study_id}/problems?year=&month=` | 멤버 | 월별 스터디 풀문제 조회 |

**반환 형식**: `monthly_problem` usecase의 문제 반환 양식을 준용한다.
각 문제는 할당받은 멤버 전원의 풀이 여부(`problem_history.solved_yn`)를 기준으로 상태가 결정된다.

| 상태 | 조건 |
|------|------|
| `solved` | 할당받은 전원이 해당 문제를 풀었음 |
| `will_solve` | 할당받은 전원이 해당 문제를 풀지 않았음 |
| `in_progress` | 일부만 푼 경우 (할당 인원 중 풀이자 > 0 이고 < 전체) |

**응답 구조** (날짜별 그룹화):
```
StudyProblemsResponse
  items: [{
    targetDate,
    problems: [{
      studyProblemId,
      problemId,
      title,
      tier,
      status,       # "solved" | "will_solve" | "in_progress"
      solveInfo: [{
        userAccountId,
        bjAccountId,
        userCode,
        solved,       # bool
        solveDate     # str | null
      }]
    }]
  }]
```

**구현 로직**: `study_problem_member` 레코드를 date_range로 조회 → 날짜별로 그룹화 →
각 멤버의 `problem_history`(solved_yn)를 일괄 조회하여 `solveInfo` 구성 및 전체 status 계산.

---

### 5.9 알림 (Notice)
| Method | URL | 권한 | 설명 |
|--------|-----|------|------|
| GET | `/user-accounts/me/notices` | 인증 | 내 알림 목록 (최신순) |
| PATCH | `/user-accounts/me/notices/read` | 인증 | 알림 일괄 읽음 처리 (body: `{noticeIds: [...]}`) |
| GET | `/user-accounts/me/notices/stream` | 인증 | SSE 연결 (실시간 알림) |

> ~~`POST /user-accounts/me/notices/read-all`~~ — `PATCH /user-accounts/me/notices/read` (noticeIds 배열)로 대체됨.

**SSE 구현 참고**: 단일 프로세스에서는 `asyncio.Queue` 기반 in-memory pub/sub.
멀티 프로세스(여러 uvicorn worker) 배포 시 Redis pub/sub으로 전환 필요. (현재 미지원)

---

### 5.10 스터디 문제 추천 (신규 API)
| Method | URL | 권한 | 설명 |
|--------|-----|------|------|
| GET | `/studies/{study_id}/recommend-problems` | 멤버 | 스터디 맥락에서 문제 추천 |

기존 `GET /user-accounts/me/problems`(개인 추천)과 별도로 운영한다.
개인 추천 API는 변경하지 않는다.

**Query params**:
- `target_user_account_id: int | None` - 추천 기준 멤버 (생략 시 본인 기준)
- `recommend_all_unsolved: bool` - `true`이면 스터디 전원이 아직 안 푼 문제만 추천

**응답**: 기존 문제 추천 응답 형식의 각 problem 객체에 `studyMemberSolveInfo` 필드 추가
```json
{
  "problems": [
    {
      "problemId": 1234,
      "title": "...",
      "tier": "...",
      "studyMemberSolveInfo": [
        {"userAccountId": 1, "bjAccountId": "user1", "solved": true},
        {"userAccountId": 2, "bjAccountId": "user2", "solved": false}
      ]
    },
    ...
  ]
}
```

**서비스 로직**: `recommand_problems_usecase`의 필터링 로직을 그대로 활용하되,
스터디 멤버 목록 중 **현재 백준 계정이 연동된 멤버**만 대상으로 `problem_history`를 조회하여 `studyMemberSolveInfo` 구성.
백준 계정 미연동 멤버는 `studyMemberSolveInfo`에서 제외한다.

---

## 6. 신규 에러 코드
> `app/core/error_codes.py` 에 추가

| 코드 | HTTP | 설명 |
|------|------|------|
| USER_CODE_EXHAUSTED | 500 | 유저 코드 고갈 |
| BJ_ACCOUNT_NOT_LINKED | 400 | 백준 계정 미연동 유저의 스터디 참여 시도 |
| STUDY_NOT_FOUND | 404 | |
| STUDY_NAME_ALREADY_TAKEN | 400 | |
| STUDY_FULL | 400 | |
| STUDY_ALREADY_MEMBER | 400 | |
| STUDY_NOT_MEMBER | 403 | |
| STUDY_OWNER_CANNOT_LEAVE | 400 | |
| STUDY_OWNER_ONLY | 403 | |
| INVITATION_NOT_FOUND | 404 | |
| INVITATION_ALREADY_SENT | 400 | |
| INVITATION_ALREADY_RESPONDED | 400 | |
| INVITATION_NOT_FOR_ME | 403 | |
| APPLICATION_NOT_FOUND | 404 | |
| APPLICATION_ALREADY_SENT | 400 | |
| APPLICATION_ALREADY_RESPONDED | 400 | |
| STUDY_PROBLEM_NOT_FOUND | 404 | |
| STUDY_PROBLEM_INVALID_TARGETS | 400 | targetUserAccountIds에 스터디 멤버가 아닌 ID 포함 |
| NOTICE_NOT_FOUND | 404 | |
| NOTICE_NOT_FOR_ME | 403 | |

---

## 7. DI Container 추가
> `app/core/containers.py`

```
wiring_config에 "app.study.presentation" 추가

신규 Singleton:
  study_repository, study_invitation_repository, study_application_repository,
  study_problem_repository, notice_repository, user_search_repository

  search_user_usecase, create_study_usecase, get_study_detail_usecase,
  search_study_usecase, update_study_usecase, delete_study_usecase,
  leave_study_usecase, kick_study_member_usecase,
  send_study_invitation_usecase, get_my_invitations_usecase,
  accept_study_invitation_usecase, reject_study_invitation_usecase,
  apply_to_study_usecase, get_study_applications_usecase,
  accept_study_application_usecase, reject_study_application_usecase,
  get_my_studies_usecase, assign_study_problem_all_usecase,
  assign_study_problem_usecase, delete_study_problem_usecase,
  get_study_problems_usecase,
  get_my_notices_usecase, mark_notice_read_usecase, mark_all_notices_read_usecase
```

기존 `recommand_problems_usecase`에 `study_repository`, `user_search_repository` 추가

---

## 8. database_models.py 추가

```python
from app.study.infra.model.study import StudyModel
from app.study.infra.model.study_member import StudyMemberModel
from app.study.infra.model.study_invitation import StudyInvitationModel
from app.study.infra.model.study_application import StudyApplicationModel
from app.study.infra.model.study_problem import StudyProblemModel
from app.study.infra.model.study_problem_member import StudyProblemMemberModel
from app.study.infra.model.notice import NoticeModel
```

---

## 9. 모듈 디렉토리 구조

```
app/study/
├── domain/entity/          study.py, study_member.py, study_invitation.py,
│                           study_application.py, study_problem.py, notice.py
├── domain/repository/      (위 6개 + user_search_repository.py)
├── application/command/    (각 usecase별 Command Pydantic 모델)
├── application/query/      study_query.py, invitation_query.py,
│                           study_problem_query.py, notice_query.py,
│                           study_recommend_query.py
├── application/usecase/    (28개 엔드포인트 대응 usecase)
├── application/service/    study_withdrawal_service.py (회원탈퇴 이벤트 핸들러)
├── infra/model/            (SQLAlchemy 모델: study, study_member, study_invitation,
│                           study_application, study_problem, study_problem_member, notice)
├── infra/mapper/           (mapper 5개)
├── infra/repository/       (repository impl 6개)
├── infra/sse/              notice_manager.py (NoticeSSEManager)
└── presentation/
    ├── controller/         study, member, invitation, application,
    │                       study_problem, notice controller
    └── schema/             request/, response/
```

---

## 10. 구현 순서

1. **UserCode 마이그레이션** - user_account 컬럼 추가 (VARCHAR 6), backfill, NOT NULL
2. **공통 타입** - 신규 VOs + Enums 추가
3. **도메인 엔티티 6개** (Study → Member → Invitation → Application → StudyProblem → Notice)
4. **SQLAlchemy 모델 6개** + `database_models.py` 등록
5. **Alembic 마이그레이션** - 6개 테이블 생성 (b1c2d3e4f5a6 이후 체인)
6. **Repository 인터페이스(ABC) + 구현체 + Mapper**
7. **Usecase 구현** (Create/Read → 멤버 관리 → 초대 → 신청 → 풀문제 → 알림)
8. **Presentation Layer** (Controller + Schema)
9. **containers.py** 등록
10. **추천 API 확장** (마지막, study_repository 완성 후)

---

## 11. DB 스키마 변경 요약

### 변경 테이블

| 테이블 | 변경 내용 |
|--------|----------|
| `user_account` | `user_code VARCHAR(6) NOT NULL UNIQUE` 컬럼 추가, `Index('idx_user_code', 'user_code')` 추가 |

### 신규 테이블

| 테이블 | 설명 | 주요 제약 |
|--------|------|----------|
| `study` | 스터디 | `UNIQUE(study_name)`, `Index(owner_user_account_id)` |
| `study_member` | 스터디 멤버 | `UNIQUE(study_id, user_account_id)` |
| `study_invitation` | 초대 | `UNIQUE(study_id, invitee_user_account_id)` |
| `study_application` | 가입신청 | - |
| `study_problem` | 스터디 풀문제 | `Index(study_id)` |
| `study_problem_member` | 문제-멤버 할당 | `study_problem_id` FK, `Index(user_account_id, target_date)` |
| `notice` | 알림 | `Index(recipient_user_account_id, is_read, created_at)` |

---

## 검증 방법

- 백준 미연동 유저로 `POST /studies` 시도 → `BJ_ACCOUNT_NOT_LINKED` 반환 확인
- `POST /studies` → 스터디 생성 + 초대 발송 확인
- `GET /user-accounts/me/invitations` → 수신된 초대 확인
- `POST /user-accounts/me/invitations/{id}/accept` → 수락 후 멤버 합류 확인
- `POST /studies/{id}/problems/all` → 전체 멤버 할당 + Notice 발송 확인
- `POST /studies/{id}/problems` (일부 멤버) → 부분 할당 확인
- `GET /studies/{id}/problems?year=2026&month=3` → 월별 풀문제 + 풀이 상태 확인
- `GET /user-accounts/me/notices/stream` → SSE 연결 후 실시간 알림 수신
- Alembic 마이그레이션: `alembic upgrade head` → 스키마 정상 생성
- 신규 유저 가입 시 `user_code` 6자리 자동 생성 확인
