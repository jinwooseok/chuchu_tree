# 스터디 도메인 구현 (초기 구현 + 리파인먼트)

**작성일**: 2026-03-03

---

## 요약

스터디 기능의 초기 구현(`app/study/` 신규)과 이후 리파인먼트 작업을 단일 PR로 통합하여 정리합니다.
28개 엔드포인트가 구현되었으며, Cases 1-5 기본 흐름 테스트가 통과하였습니다.

---

## 배경

chuchu_tree 서비스에서 친구들과 함께 백준 문제를 푸는 스터디 기능 요구사항을 충족하기 위해
Clean Architecture 패턴(domain/application/infra/presentation)을 그대로 따르는 `app/study/` 도메인을 신규 구현하였습니다.

초기 구현 이후 다음 리파인먼트 항목들이 추가로 반영되었습니다:

| 항목 | 내용 |
|------|------|
| study_problem 정규화 | `target_user_account_ids` JSON + `target_date` → `study_problem_member` 테이블 분리 |
| 방장 위임 | 방장 탈퇴/회원탈퇴 시 남은 멤버 자동 위임; 마지막 멤버 탈퇴 시 스터디 soft delete |
| 초대/신청 알림 | 초대 발송 시 피초대자 Notice+SSE, 신청 시 방장 Notice+SSE |
| 알림 일괄 읽음 | `PATCH /user-accounts/me/notices/read` (`noticeIds` 배열) 신규 |
| 스터디 문제 조회 형식 | 날짜별 그룹화 + 멤버별 풀이 현황(`solveInfo`) 포함 |
| user_code 추가 | `inviterUserCode`, `ownerUserCode`, `/bj-accounts/me`에 `userCode` 포함 |
| 초대/신청 목록 권한 완화 | 방장만 → 멤버 전체가 조회 가능 |
| 스터디 상세 비인증 | `GET /studies/{id}` — 토큰 없이도 조회 가능 |
| 회원탈퇴 연동 | `USER_ACCOUNT_WITHDRAWAL_REQUESTED` 이벤트 → study_member soft delete + 방장 위임 |
| /bj-accounts/me | `studies` 목록 + `userCode` 필드 추가 |

---

## 주요 구현 사항

### 1. 스터디 도메인 전체 아키텍처 (`app/study/` 신규)

기존 프로젝트의 Clean Architecture 패턴을 동일하게 적용하여 스터디 도메인 전체 레이어를 신규 구현하였습니다.

**도메인 엔티티 (6개)**:
- `Study` (Aggregate Root) — 스터디, 멤버 목록 포함
- `StudyMember` — 스터디-유저 관계, role(OWNER/MEMBER), joined_at
- `StudyInvitation` — 초대, invitee/inviter/status
- `StudyApplication` — 가입신청, applicant/status/message
- `StudyProblem` — 스터디 할당 문제 (study_problem_member 1:N)
- `Notice` — 알림, category별 JSON content

**Repository 인터페이스 + 구현체 (6개)**:
`StudyRepository`, `StudyInvitationRepository`, `StudyApplicationRepository`,
`StudyProblemRepository`, `NoticeRepository`, `UserSearchRepository`

**Usecase (다수)**:
총 28개 엔드포인트에 대응하는 usecase 구현.

**Alembic 마이그레이션**:
- `c3d4e5f6a7b8_add_user_code.py` — `user_account.user_code` VARCHAR(6) NOT NULL UNIQUE 추가
- `d4e5f6a7b8c9_add_study_tables.py` — study 도메인 6개 테이블 신규 생성
- `e5f6a7b8c9d0_study_problem_normalization.py` — `study_problem_member` 테이블 추가; `study_problem.target_user_account_ids`/`target_date` 컬럼 제거

---

### 2. study_problem 정규화 (`study_problem_member` 테이블 분리)

**기존**: `study_problem` 테이블에 `target_user_account_ids` JSON 컬럼 + `target_date` 단일 날짜
**변경**: `study_problem_member` 테이블로 분리 — 멤버별·날짜별 독립 관리

```
study_problem (1)
└── study_problem_member (N)
    ├── user_account_id
    └── target_date   ← 멤버마다 독립된 날짜 지정 가능
```

- 전원 할당(`/all`): 스터디 멤버 전원에게 동일 날짜로 레코드 생성
- 개인별 할당(`/problems`): `assignments` 배열로 멤버마다 날짜 독립 지정
- 회원탈퇴 시: `study_problem_member` hard delete (개인정보 완전 삭제)

`StudyProblemMemberId` VO가 `identifiers.py`에 추가되었습니다.

---

### 3. inviter_user_code 추가 (GetMyInvitations, GetStudyInvitations)

초대 목록 응답에 초대한 사람의 식별 정보를 추가하였습니다:

```json
{
  "inviterUserAccountId": 544,
  "inviterBjAccountId": "jinus7949",
  "inviterUserCode": "396056"
}
```

`InvitationQuery` 및 `InvitationItemResponse`에 `inviter_user_code` 필드 추가.
`GET /studies/{study_id}/invitations` (신규) — 스터디 멤버 전체가 조회 가능한 엔드포인트 추가.

---

### 4. 스터디 상세 비인증 조회 (`requester_user_account_id=0`)

```python
# study_controller.py
@router.get("/{study_id}", ...)
async def get_study_detail(
    study_id: int,
    usecase: GetStudyDetailUsecase = ...,  # 인증 Depends 없음
):
    query = await usecase.execute(GetStudyDetailCommand(
        study_id=study_id,
        requester_user_account_id=0,  # 비인증 사용자는 0
    ))
```

토큰 없이도 스터디 상세(`members`, `pendingInvitations`, `pendingApplications` 포함)를 조회할 수 있습니다.

---

### 5. 알림 일괄 읽음 API (`MarkNoticesReadUsecase`)

기존 `POST /read-all` 전체 읽음 방식을 `PATCH /read + noticeIds 배열` 방식으로 대체하였습니다.

```json
PATCH /user-accounts/me/notices/read
{"noticeIds": [1, 2, 3]}
```

`MarkNoticesReadUsecase` 신규 구현. `NoticeRepository.mark_by_ids(ids, user_account_id)` 메서드로
본인 소유 알림만 일괄 읽음 처리하며, 타인 알림 ID가 포함되면 `NOTICE_NOT_FOR_ME` 에러를 반환합니다.

---

### 6. SSE 알림 스트림 (`NoticeSSEManager`)

`app/study/infra/sse/notice_manager.py`에 `NoticeSSEManager` 신규 구현.

```python
class NoticeSSEManager:
    _queues: dict[int, list[asyncio.Queue]]  # user_account_id → 큐 목록

    def connect(self, user_account_id: int) -> asyncio.Queue: ...
    def disconnect(self, user_account_id: int, q: asyncio.Queue): ...
    async def push(self, user_account_id: int, data: dict): ...
```

초대/신청 발송 시 SSE 푸시를 통해 실시간 알림이 전달됩니다.
현재 single-process in-memory 구현으로, 멀티 워커 환경에서는 Redis pub/sub 전환이 필요합니다.

---

### 7. 회원탈퇴 연동 (`StudyWithdrawalService`)

`app/study/application/service/study_withdrawal_service.py` 신규 구현.

```python
@event_register_handlers()
class StudyWithdrawalService:
    @event_handler(UserAccountWithdrawalRequestedEvent)
    async def handle(self, event): ...
        # 1. study_problem_member hard delete
        # 2. study_member soft delete
        # 3. 방장이었으면 다음 멤버에게 위임 (or 스터디 soft delete)
```

`init_resources()`에서 인스턴스화하여 이벤트 핸들러 등록.

---

### 8. 문제 추천 도메인 연동

`RecommendStudyProblemsUsecase` 신규 구현 (`GET /studies/{id}/recommend-problems`).

기존 `RecommendProblemsUsecase`의 필터링 로직을 재활용하되:
- `target_user_account_id`: 추천 기준 멤버 (생략 시 본인)
- `recommend_all_unsolved`: 스터디 전원이 아직 안 푼 문제만 필터링
- 각 문제에 `studyMemberSolveInfo` (멤버별 풀이 여부) 추가

---

## 신규 파일 목록 (주요)

### Alembic 마이그레이션
- `alembic/versions/c3d4e5f6a7b8_add_user_code.py`
- `alembic/versions/d4e5f6a7b8c9_add_study_tables.py`
- `alembic/versions/e5f6a7b8c9d0_study_problem_normalization.py`

### app/study/ 도메인
```
app/study/
├── domain/entity/
│   ├── study.py
│   ├── study_member.py (StudyMember — role, joined_at)
│   ├── study_invitation.py
│   ├── study_application.py
│   ├── study_problem.py
│   └── notice.py
├── domain/repository/
│   ├── study_repository.py
│   ├── study_invitation_repository.py
│   ├── study_application_repository.py
│   ├── study_problem_repository.py
│   ├── notice_repository.py
│   └── user_search_repository.py
├── application/command/study_command.py
├── application/query/
│   ├── study_query.py
│   ├── invitation_query.py
│   ├── study_problem_query.py
│   ├── notice_query.py
│   └── study_recommend_query.py
├── application/usecase/ (28개 usecase)
├── application/service/study_withdrawal_service.py
├── infra/model/
│   ├── study.py, study_member.py, study_invitation.py
│   ├── study_application.py, study_problem.py
│   ├── study_problem_member.py (정규화)
│   └── notice.py
├── infra/mapper/ (mapper 5개)
├── infra/repository/ (impl 6개)
├── infra/sse/notice_manager.py
└── presentation/
    ├── controller/ (study, member, invitation, application, study_problem, notice)
    └── schema/ (request/, response/)
```

---

## 수정된 파일

| 파일 | 변경 내용 |
|------|----------|
| `app/common/domain/vo/identifiers.py` | `StudyId`, `StudyMemberId`, `StudyInvitationId`, `StudyApplicationId`, `StudyProblemId`, `StudyProblemMemberId`, `NoticeId` 추가 |
| `app/common/domain/enums.py` | `StudyMemberRole`, `InvitationStatus`, `ApplicationStatus`, `NoticeCategory` 추가 |
| `app/core/containers.py` | study 도메인 전체 DI 등록; `recommand_problems_usecase`에 `study_repository`, `user_search_repository` 추가 |
| `app/core/database_models.py` | study 도메인 7개 모델 import 추가 |
| `app/core/error_codes.py` | study 도메인 에러 코드 19개 추가 |
| `app/main.py` | study 라우터(study, invitation, application, member, notice, study_problem) 등록 |
| `app/user/domain/entity/user_account.py` | `user_code` 필드 추가 |
| `app/user/infra/model/user_account.py` | `user_code` 컬럼 추가 |
| `app/user/infra/mapper/user_account_mapper.py` | `user_code` 매핑 추가 |
| `app/user/infra/repository/user_account_repository_impl.py` | `insert()` 내 user_code 랜덤 생성 로직 추가 |
| `app/user/application/query/user_account_info_query.py` | `user_code` 필드 추가 |
| `app/user/application/service/user_account_application_service.py` | `user_code` 포함하여 반환 |
| `app/user/presentation/controller/user_controller.py` | `GET /user-accounts/me/studies` 포함 (member_controller로 분리) |
| `app/baekjoon/application/query/baekjoon_account_info_query.py` | `studies`, `user_code` 필드 추가 |
| `app/baekjoon/application/usecase/get_baekjoon_me_usecase.py` | studies 목록 조회 로직 추가 |
| `app/baekjoon/presentation/schema/response/get_baekjoon_me_response.py` | `studies`, `user_code` 포함 |
| `app/recommendation/application/usecase/recommend_problems_usecase.py` | `additional_excluded_problem_ids` 파라미터 추가 |

---

## API 변경 사항 요약 (28개 엔드포인트)

### 신규 엔드포인트

| Method | Path | 인증 | 설명 |
|--------|------|------|------|
| GET | `/studies/validate-name` | ✅ | 스터디 이름 중복 검증 |
| POST | `/studies` | ✅ | 스터디 생성 |
| GET | `/studies/search` | ✅ | 스터디 검색 |
| GET | `/studies/{study_id}` | ❌ | 스터디 상세 조회 (비인증 허용) |
| PATCH | `/studies/{study_id}` | ✅ | 스터디 정보 수정 |
| DELETE | `/studies/{study_id}` | ✅ | 스터디 삭제 |
| GET | `/studies/{study_id}/invitations` | ✅ | 스터디 내 초대 목록 (멤버 권한) |
| POST | `/studies/{study_id}/invitations` | ✅ | 초대 발송 |
| DELETE | `/studies/{study_id}/invitations/{id}` | ✅ | 초대 취소 |
| GET | `/user-accounts/me/invitations` | ✅ | 내 받은 초대 목록 |
| POST | `/user-accounts/me/invitations/{id}/accept` | ✅ | 초대 수락 |
| POST | `/user-accounts/me/invitations/{id}/reject` | ✅ | 초대 거절 |
| POST | `/studies/{study_id}/applications` | ✅ | 스터디 신청 |
| DELETE | `/studies/{study_id}/applications/me` | ✅ | 내 신청 취소 |
| GET | `/studies/{study_id}/applications` | ✅ | 신청 목록 조회 (멤버 권한) |
| POST | `/studies/applications/{id}/accept` | ✅ | 신청 수락 |
| POST | `/studies/applications/{id}/reject` | ✅ | 신청 거절 |
| GET | `/user-accounts/me/studies` | ✅ | 내 스터디 목록 |
| POST | `/studies/{study_id}/members/leave` | ✅ | 스터디 탈퇴 |
| DELETE | `/studies/{study_id}/members/{id}` | ✅ | 멤버 강제 퇴장 |
| GET | `/user-accounts/me/notices` | ✅ | 알림 목록 조회 |
| PATCH | `/user-accounts/me/notices/read` | ✅ | 알림 일괄 읽음 |
| GET | `/user-accounts/me/notices/stream` | ✅ | SSE 스트림 |
| POST | `/studies/{study_id}/problems/all` | ✅ | 전원 문제 할당 |
| POST | `/studies/{study_id}/problems` | ✅ | 개인별 문제 할당 |
| DELETE | `/studies/{study_id}/problems/{id}` | ✅ | 문제 할당 삭제 |
| GET | `/studies/{study_id}/problems` | ✅ | 스터디 문제 조회 |
| GET | `/studies/{study_id}/recommend-problems` | ✅ | 스터디 문제 추천 |

---

## 테스트 결과 요약

테스트 문서: `tests/docs/api_test_study_refinement_260303.md`

### 테스트 환경

| 계정 | id | bjAccountId | userCode | 역할 |
|------|----|-------------|----------|------|
| test_study_owner_a | 544 | jinus7949 | 396056 | 방장 |
| test_study_member_b | 546 | naem | - | 멤버 |
| test_study_outsider_c | 547 | (bj 미연동) | - | 비멤버 |

### 체크리스트

#### 계정 생성 / 인증
- [x] Case 1 - test_study_owner_a 테스트 계정 생성
- [x] Case 2 - test_study_member_b 테스트 계정 생성
- [x] Case 3 - test_study_outsider_c 테스트 계정 생성

#### 스터디 생성 / 상세 조회
- [x] Case 4 - test_study_owner_a가 스터디 생성 (`studyId: 1` 반환)
- [x] Case 5 - 스터디 상세 조회 (토큰 없이 — 인증 불필요)

#### 초대 — 알림 / user_code
- [ ] Case 6 - test_study_owner_a가 test_study_member_b에게 초대 발송 → Notice 생성 확인
- [ ] Case 7 - test_study_member_b의 알림 목록 조회 (STUDY_INVITATION_STATUS content 확인)
- [ ] Case 8 - test_study_member_b가 내 초대 목록 조회 (`inviterUserCode` 포함 확인)
- [ ] Case 9 - test_study_member_b가 초대 수락
- [ ] Case 10 - 스터디 내 초대 목록 조회 (멤버 권한으로 조회)

#### 신청 — 알림
- [ ] Case 11 - test_study_outsider_c가 스터디 신청 → test_study_owner_a Notice 생성 확인
- [ ] Case 12 - test_study_owner_a의 알림 목록 조회 (STUDY_APPLICATION_STATUS content 확인)
- [ ] Case 13 - 신청 목록 조회 (멤버 test_study_member_b도 조회 가능 — 권한 완화)
- [ ] Case 14 - test_study_owner_a가 신청 승인

#### 스터디 문제 할당 / 조회
- [ ] Case 15 - 전원 할당 (`POST /studies/{id}/problems/all`)
- [ ] Case 16 - 개인별 할당 (`POST /studies/{id}/problems`)
- [ ] Case 17 - 스터디 문제 조회 (날짜별 그룹 형식 + 멤버 풀이 현황)

#### user_code / 스터디 목록
- [ ] Case 18 - `/user-accounts/me/studies` 응답에 `ownerBjAccountId`, `ownerUserCode` 포함
- [ ] Case 19 - `/bj-accounts/me` 응답에 `studies` 목록 + `userCode` 포함

#### 알림 일괄 읽음
- [ ] Case 20 - 알림 일괄 읽음 처리 (`PATCH /user-accounts/me/notices/read`)
- [ ] Case 21 - 읽음 처리 후 알림 목록 조회 (`isRead: true` 확인)

#### 방장 위임
- [ ] Case 22 - 방장(test_study_owner_a) 탈퇴 → test_study_member_b에게 방장 위임 + test_study_owner_a 멤버 제거
- [ ] Case 23 - 마지막 멤버 탈퇴 시 스터디 soft delete

#### 테스트 정리
- [ ] Case 24 - 테스트 계정 전체 삭제

---

## 미완료 항목 (다음 PR 예정)

| 항목 | 설명 |
|------|------|
| SSE Manager multi-process 지원 | 현재 in-memory asyncio.Queue. Redis pub/sub 전환 필요 |
| STUDY_PROBLEMS_STATUS 알림 | 문제 할당 시 대상 멤버별 알림 발송 (현재 미발송) |
| USER_PROBLEMS_STATUS 알림 | 문제 풀이 완료 시 알림 발송 (타 도메인 이벤트 연동) |
| USER_TIER_STATUS 알림 | 티어 변경 시 알림 발송 (타 도메인 이벤트 연동) |
| Cases 6-24 테스트 | 구현 완료, 테스트 미실행 |
