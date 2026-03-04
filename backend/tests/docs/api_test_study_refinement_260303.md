# API 테스트 체크리스트 (2026-03-03 스터디 도메인)

## 요약

### 변경 범위

| 항목 | 내용 |
|------|------|
| **study_problem 정규화** | `target_user_account_ids` JSON 컬럼 → `study_problem_member` 테이블 분리. 날짜별 개인 할당 가능 |
| **방장 위임** | 방장 탈퇴/회원탈퇴 시 남은 멤버 중 첫 번째에게 자동 위임. 마지막 멤버 탈퇴 시 스터디 soft delete |
| **초대/신청 알림** | 초대 발송 시 invitee에게 Notice+SSE, 신청 시 방장에게 Notice+SSE |
| **일괄 알림 읽음** | `PATCH /user-accounts/me/notices/read` — `noticeIds` 배열로 일괄 처리 |
| **스터디 문제 조회 형식** | `GET /studies/{id}/problems` — 날짜별 그룹 + 멤버 풀이 현황 포함 |
| **user_code 추가** | 초대 목록(`inviterUserCode`), 내 스터디 목록(`ownerUserCode`), `/bj-accounts/me`(`userCode`) |
| **스터디 초대 목록 권한 완화** | `GET /studies/{id}/invitations` — 방장만 → 멤버 전체 조회 가능 |
| **신청 목록 권한 완화** | `GET /studies/{id}/applications` — 방장만 → 멤버 전체 조회 가능 |
| **스터디 상세 인증 불필요** | `GET /studies/{id}` — 비로그인(토큰 없음)도 조회 가능 |
| **회원탈퇴 시 스터디 정리** | `study_problem_member` Hard Delete, `study_member` soft delete + 방장 위임 |
| **/bj-accounts/me 스터디 목록** | 응답에 `studies: [...]` 포함 |

### 테스트 전제 조건

- **test_study_owner_a (방장)**: id=544, bjAccountId=jinus7949, userCode=396056
- **test_study_member_b (멤버)**: id=546, bjAccountId=naem
- **test_study_outsider_c (비멤버)**: id=547, bj 미연동
- **인증**: `POST /api/v1/test/auth/login` — `{"username": "..."}` 으로 로그인 후 응답 토큰 사용
- **DB 전제**: `alembic upgrade head` 완료 (`study_problem_member` 테이블 생성, `study_problem.target_user_account_ids`/`target_date` 컬럼 제거)
- **백준 연동**: test_study_owner_a, test_study_member_b는 각각 백준 계정이 연동된 상태여야 스터디 문제 할당/조회 가능 (이 테스트에서는 사전 연동 계정 사용)

### 테스트 흐름

1. 계정 3개 생성 (test_study_owner_a, test_study_member_b, test_study_outsider_c)
2. test_study_owner_a가 스터디 생성
3. test_study_owner_a가 test_study_member_b를 초대 → test_study_member_b 알림 확인
4. test_study_member_b가 초대 수락
5. test_study_outsider_c가 스터디 신청 → test_study_owner_a 알림 확인
6. test_study_owner_a가 신청 수락/거절
7. test_study_owner_a가 문제 전원 할당 (`/all`) 및 개인별 할당
8. 멤버(비방장)의 스터디 문제 조회 — 날짜별 그룹 형식 확인
9. 스터디 상세를 토큰 없이 조회 → 성공 확인
10. 멤버(test_study_member_b)가 신청 목록, 초대 목록 조회 → 권한 완화 확인
11. `/bj-accounts/me`에서 `studies` 필드 포함 확인
12. `/user-accounts/me/studies`에서 `ownerUserCode` 포함 확인
13. 알림 일괄 읽음 처리
14. 방장(test_study_owner_a) 탈퇴 시 test_study_member_b에게 방장 위임 확인
15. 마지막 멤버 탈퇴 시 스터디 soft delete 확인
16. 테스트 계정 정리

---

### 계정 생성 / 인증

- [x] Case 1 - test_study_owner_a 테스트 계정 생성
- [x] Case 2 - test_study_member_b 테스트 계정 생성
- [x] Case 3 - test_study_outsider_c 테스트 계정 생성

### 스터디 생성 / 상세 조회

- [x] Case 4 - test_study_owner_a가 스터디 생성
- [x] Case 5 - 스터디 상세 조회 (토큰 없이 — 인증 불필요)

### 초대 — 알림 / user_code

- [ ] Case 6 - test_study_owner_a가 test_study_member_b에게 초대 발송 → Notice 생성 확인
- [ ] Case 7 - test_study_member_b의 알림 목록 조회 (STUDY_INVITATION_STATUS content 확인)
- [ ] Case 8 - test_study_member_b가 내 초대 목록 조회 (`inviterUserCode` 포함 확인)
- [ ] Case 9 - test_study_member_b가 초대 수락
- [ ] Case 10 - 스터디 내 초대 목록 조회 (멤버 권한으로 조회)

### 신청 — 알림

- [ ] Case 11 - test_study_outsider_c가 스터디 신청 → test_study_owner_a Notice 생성 확인
- [ ] Case 12 - test_study_owner_a의 알림 목록 조회 (STUDY_APPLICATION_STATUS content 확인)
- [ ] Case 13 - 신청 목록 조회 (멤버 test_study_member_b도 조회 가능 — 권한 완화)
- [ ] Case 14 - test_study_owner_a가 신청 승인

### 스터디 문제 할당 / 조회

- [ ] Case 15 - 전원 할당 (`POST /studies/{id}/problems/all`)
- [ ] Case 16 - 개인별 할당 (`POST /studies/{id}/problems`)
- [ ] Case 17 - 스터디 문제 조회 (날짜별 그룹 형식 + 멤버 풀이 현황)

### user_code / 스터디 목록

- [ ] Case 18 - `/user-accounts/me/studies` 응답에 `ownerBjAccountId`, `ownerUserCode` 포함
- [ ] Case 19 - `/bj-accounts/me` 응답에 `studies` 목록 + `userCode` 포함

### 알림 일괄 읽음

- [ ] Case 20 - 알림 일괄 읽음 처리 (`PATCH /user-accounts/me/notices/read`)
- [ ] Case 21 - 읽음 처리 후 알림 목록 조회 (`isRead: true` 확인)

### 방장 위임

- [ ] Case 22 - 방장(test_study_owner_a) 탈퇴 → test_study_member_b에게 방장 위임 + test_study_owner_a 멤버 제거
- [ ] Case 23 - 마지막 멤버 탈퇴 시 스터디 soft delete

### 테스트 정리

- [ ] Case 24 - 테스트 계정 전체 삭제

---

## 테스트 상세

### 계정 생성 / 인증

---

**Case 1 - test_study_owner_a 테스트 계정 생성**

URL: `POST /api/v1/test/auth/register`

전제: local 또는 dev 환경.

예상: test_study_owner_a 계정 생성 + 로그인 성공. 결과:

Request
```
curl -X 'POST' \
  'http://localhost:8000/api/v1/test/auth/register' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "username": "test_study_owner_a"
}'
```

Response
```json
{
  "status": 200,
  "message": "ok",
  "data": {
    "user_account_id": 544,
    "username": "test_study_owner_a"
  },
  "error": {}
}
```

---

**Case 2 - test_study_member_b 테스트 계정 생성**

URL: `POST /api/v1/test/auth/register`

전제: local 또는 dev 환경.

예상: test_study_member_b 계정 생성 + 로그인 성공. 결과:

Request
```
curl -X 'POST' \
  'http://localhost:8000/api/v1/test/auth/register' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "username": "test_study_member_b"
}'
```

Response
```json
{
  "status": 200,
  "message": "ok",
  "data": {
    "user_account_id": 546,
    "username": "test_study_member_b"
  },
  "error": {}
}
```

---

**Case 3 - test_study_outsider_c 테스트 계정 생성**

URL: `POST /api/v1/test/auth/register`

전제: local 또는 dev 환경.

예상: test_study_outsider_c 계정 생성 + 로그인 성공. 결과:

Request
```
curl -X 'POST' \
  'http://localhost:8000/api/v1/test/auth/register' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "username": "test_study_outsider_c"
}'
```

Response
```json
{
  "status": 200,
  "message": "ok",
  "data": {
    "user_account_id": 547,
    "username": "test_study_outsider_c"
  },
  "error": {}
}
```

---

### 스터디 생성 / 상세 조회

---

**Case 4 - test_study_owner_a가 스터디 생성**

URL: `POST /api/v1/studies`

전제: test_study_owner_a로 로그인 상태.

예상: 스터디 생성 성공. `studyId` 반환. 결과:

Request
```
curl -X 'POST' \
  'http://localhost:8000/api/v1/studies' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "studyName": "리파인먼트 테스트 스터디",
  "description": "스터디 리파인먼트 검증용",
  "maxMembers": 5,
  "inviteeUserAccountIds": []
}'
```

Response
```json
{
  "status": 200,
  "message": "ok",
  "data": {
    "studyId": 1,
    "studyName": "리파인먼트 테스트 스터디",
    "description": "스터디 리파인먼트 검증용",
    "maxMembers": 5,
    "memberCount": 1,
    "ownerUserAccountId": 544,
    "createdAt": "2026-03-03T10:00:00"
  },
  "error": {}
}
```

---

**Case 5 - 스터디 상세 조회 (토큰 없이 — 인증 불필요)**

URL: `GET /api/v1/studies/{study_id}`

전제: 로그인 없이 요청. Case 4에서 생성된 studyId 사용.

예상: 200 성공. 비로그인 상태에서도 스터디 상세 조회 가능. 결과:

Request
```
curl -X 'GET' \
  'http://localhost:8000/api/v1/studies/1' \
  -H 'accept: application/json'
```

Response
```json
{
  "status": 200,
  "message": "ok",
  "data": {
    "studyId": 1,
    "studyName": "리파인먼트 테스트 스터디",
    "ownerUserAccountId": 544,
    "description": "스터디 리파인먼트 검증용",
    "maxMembers": 5,
    "memberCount": 1,
    "createdAt": "2026-03-03T03:01:33",
    "members": [
      {
        "userAccountId": 544,
        "bjAccountId": "jinus7949",
        "userCode": "396056",
        "role": "OWNER",
        "joinedAt": "2026-03-03T03:01:33"
      }
    ]
  },
  "error": {}
}
```

---

### 초대 — 알림 / user_code

---

**Case 6 - test_study_owner_a가 test_study_member_b에게 초대 발송 → Notice 생성 확인**

URL: `POST /api/v1/studies/{study_id}/invitations`

전제: test_study_owner_a로 로그인. inviteeUserAccountId = test_study_member_b(546).

예상: 201/200 성공. DB에서 test_study_member_b의 `notice` 레코드 생성 확인 (`category=STUDY_INVITATION_STATUS`). 결과:

Request
```
curl -X 'POST' \
  'http://localhost:8000/api/v1/studies/1/invitations' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "inviteeUserAccountId": 546
}'
```

Response
```json
{
  "status": 200,
  "message": "ok",
  "data": null,
  "error": {}
}
```

---

**Case 7 - test_study_member_b의 알림 목록 조회 (STUDY_INVITATION_STATUS content 확인)**

URL: `GET /api/v1/user-accounts/me/notices`

전제: test_study_member_b로 로그인. Case 6 직후.

예상: `items`에 `category=STUDY_INVITATION_STATUS` 알림 포함. `content.studyName`, `content.userId`(초대자 bjAccountId), `content.userCode`, `content.status="PENDING"` 포함. 결과:

Request
```
curl -X 'GET' \
  'http://localhost:8000/api/v1/user-accounts/me/notices' \
  -H 'accept: application/json'
```

Response
```json
{
  "status": 200,
  "message": "ok",
  "data": {
    "items": [
      {
        "noticeId": 1,
        "category": "STUDY_INVITATION_STATUS",
        "isRead": false,
        "createdAt": "2026-03-03T10:01:00",
        "content": {
          "studyName": "리파인먼트 테스트 스터디",
          "userId": "jinus7949",
          "userCode": "396056",
          "status": "PENDING"
        }
      }
    ]
  },
  "error": {}
}
```

---

**Case 8 - test_study_member_b가 내 초대 목록 조회 (`inviterUserCode` 포함 확인)**

URL: `GET /api/v1/user-accounts/me/invitations`

전제: test_study_member_b로 로그인. Case 6 직후.

예상: 초대 목록에 `inviterUserAccountId`, `inviterBjAccountId`, `inviterUserCode` 필드 포함. 결과:

Request
```
curl -X 'GET' \
  'http://localhost:8000/api/v1/user-accounts/me/invitations' \
  -H 'accept: application/json'
```

Response
```json
{
  "status": 200,
  "message": "ok",
  "data": {
    "items": [
      {
        "invitationId": 1,
        "studyId": 1,
        "studyName": "리파인먼트 테스트 스터디",
        "inviterUserAccountId": 544,
        "inviterBjAccountId": "jinus7949",
        "inviterUserCode": "396056",
        "status": "PENDING",
        "createdAt": "2026-03-03T10:01:00"
      }
    ]
  },
  "error": {}
}
```

---

**Case 9 - test_study_member_b가 초대 수락**

URL: `POST /api/v1/user-accounts/me/invitations/{invitation_id}/accept`

전제: test_study_member_b로 로그인. invitationId = 1.

예상: 성공, data=null. DB에서 `study_member`에 test_study_member_b 추가 확인. 결과:

Request
```
curl -X 'POST' \
  'http://localhost:8000/api/v1/user-accounts/me/invitations/1/accept' \
  -H 'accept: application/json' \
  -d ''
```

Response
```json
{
  "status": 200,
  "message": "ok",
  "data": null,
  "error": {}
}
```

---

**Case 10 - 스터디에서 초대 목록 조회 (멤버 권한으로 조회)**

URL: `GET /api/v1/studies/{study_id}/invitations`

전제: test_study_member_b로 로그인 (방장이 아닌 일반 멤버). Case 9 이후 test_study_member_b가 멤버로 가입한 상태. test_study_owner_a가 추가로 다른 유저에게 초대 발송한 상태.

예상: 멤버(비방장)도 200 성공. 스터디에서 발송 중인 초대 목록 반환. 결과:

Request
```
curl -X 'GET' \
  'http://localhost:8000/api/v1/studies/1/invitations' \
  -H 'accept: application/json'
```

Response
```json
{
  "status": 200,
  "message": "ok",
  "data": {
    "items": []
  },
  "error": {}
}
```

---

### 신청 — 알림

---

**Case 11 - test_study_outsider_c가 스터디 신청 → test_study_owner_a Notice 생성 확인**

URL: `POST /api/v1/studies/{study_id}/applications`

전제: test_study_outsider_c로 로그인. **test_study_outsider_c는 bj 미연동 → 신청 불가. 별도 bj 연동 계정으로 대체 테스트 필요.**

예상: 성공. DB에서 test_study_owner_a의 `notice` 레코드 생성 확인 (`category=STUDY_APPLICATION_STATUS`). 결과:

Request
```
curl -X 'POST' \
  'http://localhost:8000/api/v1/studies/1/applications' \
  -H 'accept: application/json' \
  -d ''
```

Response
```json
{
  "status": 200,
  "message": "ok",
  "data": null,
  "error": {}
}
```

---

**Case 12 - test_study_owner_a의 알림 목록 조회 (STUDY_APPLICATION_STATUS content 확인)**

URL: `GET /api/v1/user-accounts/me/notices`

전제: test_study_owner_a로 로그인. Case 11 직후.

예상: `items`에 `category=STUDY_APPLICATION_STATUS` 알림 포함. `content.studyName`, `content.status="PENDING"` 포함. 결과:

Request
```
curl -X 'GET' \
  'http://localhost:8000/api/v1/user-accounts/me/notices' \
  -H 'accept: application/json'
```

Response
```json
{
  "status": 200,
  "message": "ok",
  "data": {
    "items": [
      {
        "noticeId": 2,
        "category": "STUDY_APPLICATION_STATUS",
        "isRead": false,
        "createdAt": "2026-03-03T10:05:00",
        "content": {
          "studyName": "리파인먼트 테스트 스터디",
          "status": "PENDING"
        }
      }
    ]
  },
  "error": {}
}
```

---

**Case 13 - 신청 목록 조회 (멤버 test_study_member_b도 조회 가능 — 권한 완화)**

URL: `GET /api/v1/studies/{study_id}/applications`

전제: test_study_member_b로 로그인 (방장이 아닌 일반 멤버). Case 11 이후.

예상: 멤버(비방장)도 200 성공. 신청 목록 반환. 결과:

Request
```
curl -X 'GET' \
  'http://localhost:8000/api/v1/studies/1/applications' \
  -H 'accept: application/json'
```

Response
```json
{
  "status": 200,
  "message": "ok",
  "data": {
    "items": [
      {
        "applicationId": 1,
        "userAccountId": 547,
        "bjAccountId": "(test_study_outsider_c bj 미연동 — 신청 불가)",
        "status": "PENDING",
        "createdAt": "2026-03-03T10:05:00"
      }
    ]
  },
  "error": {}
}
```

---

**Case 14 - test_study_owner_a가 신청 승인**

URL: `POST /api/v1/studies/{study_id}/applications/{application_id}/accept`

전제: test_study_owner_a로 로그인. applicationId = 1.

예상: 성공. DB에서 `study_member`에 test_study_outsider_c 추가 확인. 결과:

Request
```
curl -X 'POST' \
  'http://localhost:8000/api/v1/studies/1/applications/1/accept' \
  -H 'accept: application/json' \
  -d ''
```

Response
```json
{
  "status": 200,
  "message": "ok",
  "data": null,
  "error": {}
}
```

---

### 스터디 문제 할당 / 조회

---

**Case 15 - 전원 할당 (`POST /studies/{id}/problems/all`)**

URL: `POST /api/v1/studies/{study_id}/problems/all`

전제: test_study_owner_a로 로그인. 스터디에 test_study_owner_a, test_study_member_b, test_study_outsider_c 총 3명 멤버. `targetDate` 오늘 날짜.

예상: 성공. DB에서 `study_problem_member` 레코드 3개 생성 확인 (멤버 수만큼). 결과:

Request
```
curl -X 'POST' \
  'http://localhost:8000/api/v1/studies/1/problems/all' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "problemId": 1000,
  "targetDate": "2026-03-03"
}'
```

Response
```json
{
  "status": 200,
  "message": "ok",
  "data": null,
  "error": {}
}
```

---

**Case 16 - 개인별 할당 (`POST /studies/{id}/problems`)**

URL: `POST /api/v1/studies/{study_id}/problems`

전제: test_study_owner_a로 로그인. test_study_owner_a에게 1001번, test_study_member_b에게 1001번 문제를 서로 다른 날짜로 할당.

예상: 성공. DB에서 `study_problem_member` 레코드 2개 생성 확인. 날짜/문제가 멤버마다 독립적. 결과:

Request
```
curl -X 'POST' \
  'http://localhost:8000/api/v1/studies/1/problems' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "problemId": 1001,
  "assignments": [
    {"userAccountId": 544, "targetDate": "2026-03-04"},
    {"userAccountId": 546, "targetDate": "2026-03-05"}
  ]
}'
```

Response
```json
{
  "status": 200,
  "message": "ok",
  "data": null,
  "error": {}
}
```

---

**Case 17 - 스터디 문제 조회 (날짜별 그룹 형식 + 멤버 풀이 현황)**

URL: `GET /api/v1/studies/{study_id}/problems?year=2026&month=3`

전제: test_study_owner_a로 로그인. Case 15, 16 이후.

예상: `items` 배열로 날짜별 그룹화. 각 `targetDate`마다 `problems` 배열. 각 문제에 `solveInfo` 배열(멤버별 풀이 여부). `solved`, `solveDate`, `userCode` 포함. 결과:

Request
```
curl -X 'GET' \
  'http://localhost:8000/api/v1/studies/1/problems?year=2026&month=3' \
  -H 'accept: application/json'
```

Response
```json
{
  "status": 200,
  "message": "ok",
  "data": {
    "items": [
      {
        "targetDate": "2026-03-03",
        "problems": [
          {
            "studyProblemId": 1,
            "problemId": 1000,
            "title": "A+B",
            "tier": 1,
            "solveInfo": [
              {
                "userAccountId": 544,
                "bjAccountId": "jinus7949",
                "userCode": "396056",
                "solved": true,
                "solveDate": null
              },
              {
                "userAccountId": 546,
                "bjAccountId": "naem",
                "userCode": "208346",
                "solved": true,
                "solveDate": null
              },
              {
                "userAccountId": 547,
                "bjAccountId": "happynj2697",
                "userCode": "659311",
                "solved": true,
                "solveDate": null
              }
            ],
            "status": "solved"
          }
        ]
      },
      {
        "targetDate": "2026-03-04",
        "problems": [
          {
            "studyProblemId": 2,
            "problemId": 1001,
            "title": "A-B",
            "tier": 1,
            "solveInfo": [
              {
                "userAccountId": 544,
                "bjAccountId": "jinus7949",
                "userCode": "396056",
                "solved": true,
                "solveDate": null
              }
            ],
            "status": "solved"
          }
        ]
      },
      {
        "targetDate": "2026-03-05",
        "problems": [
          {
            "studyProblemId": 2,
            "problemId": 1001,
            "title": "A-B",
            "tier": 1,
            "solveInfo": [
              {
                "userAccountId": 546,
                "bjAccountId": "naem",
                "userCode": "208346",
                "solved": true,
                "solveDate": null
              }
            ],
            "status": "solved"
          }
        ]
      }
    ]
  },
  "error": {}
}
```

---

### user_code / 스터디 목록

---

**Case 18 - `/user-accounts/me/studies` 응답에 `ownerBjAccountId`, `ownerUserCode` 포함**

URL: `GET /api/v1/user-accounts/me/studies`

전제: test_study_member_b로 로그인. test_study_member_b가 Case 4의 스터디에 가입된 상태.

예상: 내 스터디 목록에 `ownerBjAccountId`, `ownerUserCode` 필드 포함. 결과:

Request
```
curl -X 'GET' \
  'http://localhost:8000/api/v1/user-accounts/me/studies' \
  -H 'accept: application/json'
```

Response
```json
{
  "status": 200,
  "message": "ok",
  "data": {
    "items": [
      {
        "studyId": 1,
        "studyName": "리파인먼트 테스트 스터디",
        "ownerUserAccountId": 544,
        "ownerBjAccountId": "jinus7949",
        "ownerUserCode": "396056",
        "description": "스터디 리파인먼트 검증용",
        "maxMembers": 5,
        "memberCount": 3,
        "createdAt": "2026-03-03T10:00:00"
      }
    ]
  },
  "error": {}
}
```

---

**Case 19 - `/bj-accounts/me` 응답에 `studies` 목록 + `userCode` 포함**

URL: `GET /api/v1/bj-accounts/me`

전제: test_study_owner_a로 로그인. test_study_owner_a는 백준 계정 연동 상태.

예상: `userAccount.userCode` 필드 포함. `studies` 배열에 참여 중인 스터디 목록 포함 (`ownerBjAccountId`, `ownerUserCode` 포함). 결과:

Request
```
curl -X 'GET' \
  'http://localhost:8000/api/v1/bj-accounts/me' \
  -H 'accept: application/json'
```

Response
```json
{
  "status": 200,
  "message": "ok",
  "data": {
    "userAccount": {
      "userAccountId": 544,
      "profileImageUrl": null,
      "target": {
        "targetId": 1,
        "targetCode": "DAILY",
        "targetDisplayName": "매일"
      },
      "registeredAt": "2026-03-03T10:00:00",
      "isSynced": true,
      "userCode": "396056"
    },
    "bjAccount": {
      "bjAccountId": "jinus7949",
      "stat": {
        "tierId": 1,
        "tierName": "B5",
        "longestStreak": 10,
        "rating": 700,
        "class": 1,
        "tierStartDate": null
      },
      "streaks": [],
      "registeredAt": "2026-03-01T00:00:00"
    },
    "linkedAt": "2026-03-01T00:00:00",
    "studies": [
      {
        "studyId": 1,
        "studyName": "리파인먼트 테스트 스터디",
        "ownerUserAccountId": 544,
        "ownerBjAccountId": "jinus7949",
        "ownerUserCode": "396056",
        "description": "스터디 리파인먼트 검증용",
        "maxMembers": 5,
        "memberCount": 3,
        "createdAt": "2026-03-03T10:00:00"
      }
    ]
  },
  "error": {}
}
```

---

### 알림 일괄 읽음

---

**Case 20 - 알림 일괄 읽음 처리 (`PATCH /user-accounts/me/notices/read`)**

URL: `PATCH /api/v1/user-accounts/me/notices/read`

전제: test_study_member_b로 로그인. Case 7에서 확인한 알림 ID 목록 사용.

예상: 성공, data=null. DB에서 `notice.is_read=1` 확인. 결과:

Request
```
curl -X 'PATCH' \
  'http://localhost:8000/api/v1/user-accounts/me/notices/read' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "noticeIds": [1]
}'
```

Response
```json
{
  "status": 200,
  "message": "ok",
  "data": null,
  "error": {}
}
```

---

**Case 21 - 읽음 처리 후 알림 목록 조회 (`isRead: true` 확인)**

URL: `GET /api/v1/user-accounts/me/notices`

전제: test_study_member_b로 로그인. Case 20 직후.

예상: 해당 알림의 `isRead: true`로 변경 확인. 결과:

Request
```
curl -X 'GET' \
  'http://localhost:8000/api/v1/user-accounts/me/notices' \
  -H 'accept: application/json'
```

Response
```json
{
  "status": 200,
  "message": "ok",
  "data": {
    "items": [
      {
        "noticeId": 1,
        "category": "STUDY_INVITATION_STATUS",
        "isRead": true,
        "createdAt": "2026-03-03T10:01:00",
        "content": {
          "studyName": "리파인먼트 테스트 스터디",
          "userId": "jinus7949",
          "userCode": "396056",
          "status": "PENDING"
        }
      }
    ]
  },
  "error": {}
}
```

---

### 방장 위임

---

**Case 22 - 방장(test_study_owner_a) 탈퇴 → test_study_member_b에게 방장 위임 + test_study_owner_a 멤버 제거**

URL: `POST /api/v1/studies/{study_id}/members/leave`

전제: test_study_owner_a로 로그인. 스터디에 test_study_owner_a(방장), test_study_member_b, test_study_outsider_c 존재.

예상: 성공. DB에서 test_study_member_b의 `study_member.role=OWNER`, test_study_owner_a의 `study_member.deleted_at` 설정 확인. 스터디 `owner_user_account_id = test_study_member_b` 변경 확인. 결과:

Request
```
curl -X 'POST' \
  'http://localhost:8000/api/v1/studies/1/members/leave' \
  -H 'accept: application/json' \
  -d ''
```

Response
```json
{
  "status": 200,
  "message": "ok",
  "data": null,
  "error": {}
}
```

검증 (스터디 상세 재조회):
```
curl -X 'GET' \
  'http://localhost:8000/api/v1/studies/1' \
  -H 'accept: application/json'
```

예상 응답 (방장이 test_study_member_b로 변경됨):
```json
{
  "data": {
    "studyId": 1,
    "ownerUserAccountId": 546,
    "members": [
      {"userAccountId": 546, "role": "OWNER"},
      {"userAccountId": 547, "role": "MEMBER"}
    ]
  }
}
```

---

**Case 23 - 마지막 멤버 탈퇴 시 스터디 soft delete**

URL: `POST /api/v1/studies/{study_id}/members/leave`

전제: 별도 테스트용 스터디 생성 (멤버: test_study_member_b 혼자). test_study_member_b가 방장인 상태.

예상: 성공. DB에서 `study.deleted_at` 설정 확인 (soft delete). 결과:

Request
```
# 1. 테스트용 스터디 생성 (test_study_member_b가 방장)
curl -X 'POST' \
  'http://localhost:8000/api/v1/studies' \
  -H 'Content-Type: application/json' \
  -d '{"studyName": "혼자스터디", "maxMembers": 5}'

# 2. test_study_member_b 탈퇴 (마지막 멤버)
curl -X 'POST' \
  'http://localhost:8000/api/v1/studies/2/members/leave' \
  -H 'accept: application/json' \
  -d ''
```

Response (탈퇴 요청)
```json
{
  "status": 200,
  "message": "ok",
  "data": null,
  "error": {}
}
```

검증: DB에서 `SELECT deleted_at FROM study WHERE study_id=2;` → `deleted_at IS NOT NULL` 확인.

---