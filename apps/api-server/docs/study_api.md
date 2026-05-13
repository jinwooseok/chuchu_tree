# 스터디 도메인 API 명세서

**작성일**: 2026-03-03
**Base URL**: `http://localhost:8000/api/v1`
**인증 방식**: Bearer Token (Authorization 헤더)
**응답 공통 포맷**:
```json
{
  "status": 200,
  "message": "ok",
  "data": { ... },
  "error": {}
}
```

---

## 목차

1. [스터디 관리](#1-스터디-관리)
2. [초대 (Invitation)](#2-초대-invitation)
3. [신청 (Application)](#3-신청-application)
4. [멤버 관리](#4-멤버-관리)
5. [알림 (Notice)](#5-알림-notice)
6. [스터디 문제](#6-스터디-문제)

---

## 1. 스터디 관리

### 1.1 스터디 이름 중복 검증

```
GET /studies/validate-name
```

**인증**: 필요
**권한**: 인증된 사용자

**Query Parameters**

| 파라미터 | 타입 | 필수 | 설명 |
|---------|------|------|------|
| name | string | ✅ | 검증할 스터디명 |

**Response**

```json
{
  "status": 200,
  "message": "ok",
  "data": {
    "available": true
  },
  "error": {}
}
```

| 필드 | 타입 | 설명 |
|------|------|------|
| available | boolean | `true` = 사용 가능, `false` = 이미 사용 중 |

---

### 1.2 스터디 생성

```
POST /studies
```

**인증**: 필요
**권한**: 인증된 사용자 (백준 계정 연동 필수)

**Request Body**

```json
{
  "studyName": "알고리즘 스터디",
  "description": "매일 한 문제씩 풉니다",
  "maxMembers": 10,
  "inviteeUserAccountIds": [2, 3]
}
```

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| studyName | string | ✅ | 스터디명 (max 50, unique) |
| description | string \| null | ❌ | 설명 (max 200) |
| maxMembers | integer | ❌ | 최대 인원 (default 10) |
| inviteeUserAccountIds | integer[] | ❌ | 생성 시 즉시 초대할 유저 ID 목록 |

**Response**

```json
{
  "status": 200,
  "message": "ok",
  "data": {
    "studyId": 1,
    "studyName": "알고리즘 스터디",
    "ownerUserAccountId": 544,
    "description": "매일 한 문제씩 풉니다",
    "maxMembers": 10,
    "memberCount": 1,
    "createdAt": "2026-03-03T10:00:00"
  },
  "error": {}
}
```

**에러 코드**

| 코드 | HTTP | 상황 |
|------|------|------|
| BJ_ACCOUNT_NOT_LINKED | 400 | 요청자 또는 초대 대상자의 백준 계정 미연동 |
| STUDY_NAME_ALREADY_TAKEN | 400 | 스터디명 중복 |

---

### 1.3 스터디 검색

```
GET /studies/search
```

**인증**: 필요
**권한**: 인증된 사용자

**Query Parameters**

| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|---------|------|------|--------|------|
| keyword | string | ✅ | - | 검색어 (스터디명 / 방장 bjAccountId / 방장 userCode) |
| limit | integer | ❌ | 5 | 최대 반환 개수 |

**Response**

```json
{
  "status": 200,
  "message": "ok",
  "data": {
    "studies": [
      {
        "studyId": 1,
        "studyName": "알고리즘 스터디",
        "ownerBjAccountId": "startlink",
        "ownerUserCode": "000000",
        "memberCount": 3
      }
    ]
  },
  "error": {}
}
```

---

### 1.4 스터디 상세 조회

```
GET /studies/{study_id}
```

**인증**: 불필요 (비로그인도 조회 가능)
**권한**: 없음

**Path Parameters**

| 파라미터 | 타입 | 설명 |
|---------|------|------|
| study_id | integer | 스터디 ID |

**Response**

```json
{
  "status": 200,
  "message": "ok",
  "data": {
    "studyId": 1,
    "studyName": "알고리즘 스터디",
    "ownerUserAccountId": 544,
    "description": "매일 한 문제씩 풉니다",
    "maxMembers": 10,
    "memberCount": 2,
    "createdAt": "2026-03-03T10:00:00",
    "members": [
      {
        "userAccountId": 544,
        "bjAccountId": "jinus7949",
        "userCode": "396056",
        "role": "OWNER",
        "joinedAt": "2026-03-03T10:00:00"
      },
      {
        "userAccountId": 546,
        "bjAccountId": "naem",
        "userCode": "208346",
        "role": "MEMBER",
        "joinedAt": "2026-03-03T10:05:00"
      }
    ],
    "pendingInvitations": [
      {
        "invitationId": 1,
        "inviteeUserAccountId": 547,
        "inviteeBjAccountId": "testuser",
        "inviteeUserCode": "123456",
        "createdAt": "2026-03-03T10:10:00"
      }
    ],
    "pendingApplications": [
      {
        "applicationId": 2,
        "applicantUserAccountId": 548,
        "applicantBjAccountId": "applicant",
        "applicantUserCode": "654321",
        "createdAt": "2026-03-03T10:15:00"
      }
    ]
  },
  "error": {}
}
```

**에러 코드**

| 코드 | HTTP | 상황 |
|------|------|------|
| STUDY_NOT_FOUND | 404 | 해당 스터디 없음 |

---

### 1.5 스터디 수정

```
PATCH /studies/{study_id}
```

**인증**: 필요
**권한**: 방장(OWNER)

**Path Parameters**

| 파라미터 | 타입 | 설명 |
|---------|------|------|
| study_id | integer | 스터디 ID |

**Request Body**

```json
{
  "description": "새 설명",
  "maxMembers": 15
}
```

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| description | string \| null | ❌ | 새 설명 |
| maxMembers | integer \| null | ❌ | 새 최대 인원 |

**Response**

```json
{
  "status": 200,
  "message": "ok",
  "data": null,
  "error": {}
}
```

**에러 코드**

| 코드 | HTTP | 상황 |
|------|------|------|
| STUDY_NOT_FOUND | 404 | 스터디 없음 |
| STUDY_OWNER_ONLY | 403 | 방장이 아님 |

---

### 1.6 스터디 삭제

```
DELETE /studies/{study_id}
```

**인증**: 필요
**권한**: 방장(OWNER)

**Path Parameters**

| 파라미터 | 타입 | 설명 |
|---------|------|------|
| study_id | integer | 스터디 ID |

**Response**

```json
{
  "status": 200,
  "message": "ok",
  "data": null,
  "error": {}
}
```

**에러 코드**

| 코드 | HTTP | 상황 |
|------|------|------|
| STUDY_NOT_FOUND | 404 | 스터디 없음 |
| STUDY_OWNER_ONLY | 403 | 방장이 아님 |

---

## 2. 초대 (Invitation)

### 2.1 스터디 내 초대 목록 조회

```
GET /studies/{study_id}/invitations
```

**인증**: 필요
**권한**: 스터디 멤버 (방장·일반멤버 모두 가능)

**Path Parameters**

| 파라미터 | 타입 | 설명 |
|---------|------|------|
| study_id | integer | 스터디 ID |

**Response**

```json
{
  "status": 200,
  "message": "ok",
  "data": {
    "invitations": [
      {
        "invitationId": 1,
        "studyId": 1,
        "studyName": "알고리즘 스터디",
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

**에러 코드**

| 코드 | HTTP | 상황 |
|------|------|------|
| STUDY_NOT_FOUND | 404 | 스터디 없음 |
| STUDY_NOT_MEMBER | 403 | 스터디 멤버가 아님 |

---

### 2.2 초대 발송

```
POST /studies/{study_id}/invitations
```

**인증**: 필요
**권한**: 방장(OWNER)

**Path Parameters**

| 파라미터 | 타입 | 설명 |
|---------|------|------|
| study_id | integer | 스터디 ID |

**Request Body**

```json
{
  "inviteeUserAccountId": 546
}
```

**Response**

```json
{
  "status": 200,
  "message": "ok",
  "data": null,
  "error": {}
}
```

**부수 효과**: 피초대자에게 `STUDY_INVITATION_STATUS` Notice 생성 + SSE 푸시

**에러 코드**

| 코드 | HTTP | 상황 |
|------|------|------|
| STUDY_NOT_FOUND | 404 | 스터디 없음 |
| STUDY_OWNER_ONLY | 403 | 방장이 아님 |
| BJ_ACCOUNT_NOT_LINKED | 400 | 피초대자 백준 미연동 |
| INVITATION_ALREADY_SENT | 400 | 이미 PENDING 초대 존재 |
| STUDY_ALREADY_MEMBER | 400 | 이미 멤버 |

---

### 2.3 초대 취소

```
DELETE /studies/{study_id}/invitations/{invitation_id}
```

**인증**: 필요
**권한**: 방장(OWNER)

**Path Parameters**

| 파라미터 | 타입 | 설명 |
|---------|------|------|
| study_id | integer | 스터디 ID |
| invitation_id | integer | 초대 ID |

**Response**

```json
{
  "status": 200,
  "message": "ok",
  "data": null,
  "error": {}
}
```

**에러 코드**

| 코드 | HTTP | 상황 |
|------|------|------|
| INVITATION_NOT_FOUND | 404 | 초대 없음 |
| STUDY_OWNER_ONLY | 403 | 방장이 아님 |

---

### 2.4 내 초대 목록 조회

```
GET /user-accounts/me/invitations
```

**인증**: 필요
**권한**: 인증된 사용자 (자신이 받은 초대만 조회)

**Response**

```json
{
  "status": 200,
  "message": "ok",
  "data": {
    "invitations": [
      {
        "invitationId": 1,
        "studyId": 1,
        "studyName": "알고리즘 스터디",
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

| 필드 | 설명 |
|------|------|
| inviterUserAccountId | 초대한 사람의 userAccountId |
| inviterBjAccountId | 초대한 사람의 백준 ID |
| inviterUserCode | 초대한 사람의 userCode (6자리) |
| status | `PENDING` \| `ACCEPTED` \| `REJECTED` |

---

### 2.5 초대 수락

```
POST /user-accounts/me/invitations/{invitation_id}/accept
```

**인증**: 필요
**권한**: 초대받은 본인

**Path Parameters**

| 파라미터 | 타입 | 설명 |
|---------|------|------|
| invitation_id | integer | 초대 ID |

**Response**

```json
{
  "status": 200,
  "message": "ok",
  "data": null,
  "error": {}
}
```

**부수 효과**: 스터디 멤버로 추가, 방장에게 Notice 발송

**에러 코드**

| 코드 | HTTP | 상황 |
|------|------|------|
| INVITATION_NOT_FOUND | 404 | 초대 없음 |
| INVITATION_NOT_FOR_ME | 403 | 내 초대가 아님 |
| INVITATION_ALREADY_RESPONDED | 400 | 이미 처리된 초대 |
| BJ_ACCOUNT_NOT_LINKED | 400 | 수락자 백준 미연동 |
| STUDY_FULL | 400 | 스터디 정원 초과 |

---

### 2.6 초대 거절

```
POST /user-accounts/me/invitations/{invitation_id}/reject
```

**인증**: 필요
**권한**: 초대받은 본인

**Path Parameters**

| 파라미터 | 타입 | 설명 |
|---------|------|------|
| invitation_id | integer | 초대 ID |

**Response**

```json
{
  "status": 200,
  "message": "ok",
  "data": null,
  "error": {}
}
```

**에러 코드**

| 코드 | HTTP | 상황 |
|------|------|------|
| INVITATION_NOT_FOUND | 404 | 초대 없음 |
| INVITATION_NOT_FOR_ME | 403 | 내 초대가 아님 |
| INVITATION_ALREADY_RESPONDED | 400 | 이미 처리된 초대 |

---

## 3. 신청 (Application)

### 3.1 스터디 신청

```
POST /studies/{study_id}/applications
```

**인증**: 필요
**권한**: 인증된 사용자 (비멤버, 백준 계정 연동 필수)

**Path Parameters**

| 파라미터 | 타입 | 설명 |
|---------|------|------|
| study_id | integer | 스터디 ID |

**Request Body**

```json
{
  "message": "열심히 하겠습니다"
}
```

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| message | string \| null | ❌ | 가입 메시지 (max 300) |

**Response**

```json
{
  "status": 200,
  "message": "ok",
  "data": null,
  "error": {}
}
```

**부수 효과**: 방장에게 `STUDY_APPLICATION_STATUS` Notice 생성 + SSE 푸시

**에러 코드**

| 코드 | HTTP | 상황 |
|------|------|------|
| STUDY_NOT_FOUND | 404 | 스터디 없음 |
| BJ_ACCOUNT_NOT_LINKED | 400 | 백준 미연동 |
| STUDY_ALREADY_MEMBER | 400 | 이미 멤버 |
| APPLICATION_ALREADY_SENT | 400 | PENDING 신청 이미 존재 |
| STUDY_FULL | 400 | 정원 초과 |

---

### 3.2 내 신청 취소

```
DELETE /studies/{study_id}/applications/me
```

**인증**: 필요
**권한**: 신청자 본인

**Path Parameters**

| 파라미터 | 타입 | 설명 |
|---------|------|------|
| study_id | integer | 스터디 ID |

**Response**

```json
{
  "status": 200,
  "message": "ok",
  "data": null,
  "error": {}
}
```

**에러 코드**

| 코드 | HTTP | 상황 |
|------|------|------|
| APPLICATION_NOT_FOUND | 404 | 신청 없음 |

---

### 3.3 신청 목록 조회

```
GET /studies/{study_id}/applications
```

**인증**: 필요
**권한**: 스터디 멤버 (방장·일반멤버 모두 가능)

**Path Parameters**

| 파라미터 | 타입 | 설명 |
|---------|------|------|
| study_id | integer | 스터디 ID |

**Response**

```json
{
  "status": 200,
  "message": "ok",
  "data": {
    "applications": [
      {
        "applicationId": 1,
        "applicantUserAccountId": 547,
        "applicantBjAccountId": "testuser",
        "applicantUserCode": "654321",
        "createdAt": "2026-03-03T10:05:00"
      }
    ]
  },
  "error": {}
}
```

**에러 코드**

| 코드 | HTTP | 상황 |
|------|------|------|
| STUDY_NOT_FOUND | 404 | 스터디 없음 |
| STUDY_NOT_MEMBER | 403 | 멤버가 아님 |

---

### 3.4 신청 수락

```
POST /studies/applications/{application_id}/accept
```

**인증**: 필요
**권한**: 방장(OWNER)

**Path Parameters**

| 파라미터 | 타입 | 설명 |
|---------|------|------|
| application_id | integer | 신청 ID |

**Response**

```json
{
  "status": 200,
  "message": "ok",
  "data": null,
  "error": {}
}
```

**부수 효과**: 신청자를 스터디 멤버로 추가, 신청자에게 Notice 발송

**에러 코드**

| 코드 | HTTP | 상황 |
|------|------|------|
| APPLICATION_NOT_FOUND | 404 | 신청 없음 |
| STUDY_OWNER_ONLY | 403 | 방장이 아님 |
| APPLICATION_ALREADY_RESPONDED | 400 | 이미 처리된 신청 |
| STUDY_FULL | 400 | 정원 초과 |

---

### 3.5 신청 거절

```
POST /studies/applications/{application_id}/reject
```

**인증**: 필요
**권한**: 방장(OWNER)

**Path Parameters**

| 파라미터 | 타입 | 설명 |
|---------|------|------|
| application_id | integer | 신청 ID |

**Response**

```json
{
  "status": 200,
  "message": "ok",
  "data": null,
  "error": {}
}
```

**에러 코드**

| 코드 | HTTP | 상황 |
|------|------|------|
| APPLICATION_NOT_FOUND | 404 | 신청 없음 |
| STUDY_OWNER_ONLY | 403 | 방장이 아님 |
| APPLICATION_ALREADY_RESPONDED | 400 | 이미 처리된 신청 |

---

## 4. 멤버 관리

### 4.1 내 스터디 목록

```
GET /user-accounts/me/studies
```

**인증**: 필요
**권한**: 인증된 사용자

**Response**

```json
{
  "status": 200,
  "message": "ok",
  "data": {
    "studies": [
      {
        "studyId": 1,
        "studyName": "알고리즘 스터디",
        "ownerUserAccountId": 544,
        "ownerBjAccountId": "jinus7949",
        "ownerUserCode": "396056",
        "description": "매일 한 문제씩 풉니다",
        "maxMembers": 10,
        "memberCount": 2,
        "createdAt": "2026-03-03T10:00:00"
      }
    ]
  },
  "error": {}
}
```

| 필드 | 설명 |
|------|------|
| ownerBjAccountId | 방장의 백준 ID |
| ownerUserCode | 방장의 userCode (6자리) |

---

### 4.2 스터디 탈퇴

```
POST /studies/{study_id}/members/leave
```

**인증**: 필요
**권한**: 스터디 멤버

**Path Parameters**

| 파라미터 | 타입 | 설명 |
|---------|------|------|
| study_id | integer | 스터디 ID |

**Response**

```json
{
  "status": 200,
  "message": "ok",
  "data": null,
  "error": {}
}
```

**부수 효과**:
- 방장이 탈퇴하는 경우: 남은 멤버 중 첫 번째에게 방장 위임
- 마지막 멤버가 탈퇴하는 경우: 스터디 soft delete

**에러 코드**

| 코드 | HTTP | 상황 |
|------|------|------|
| STUDY_NOT_FOUND | 404 | 스터디 없음 |
| STUDY_NOT_MEMBER | 403 | 멤버가 아님 |

---

### 4.3 멤버 강제 퇴장

```
DELETE /studies/{study_id}/members/{member_user_account_id}
```

**인증**: 필요
**권한**: 방장(OWNER)

**Path Parameters**

| 파라미터 | 타입 | 설명 |
|---------|------|------|
| study_id | integer | 스터디 ID |
| member_user_account_id | integer | 강퇴할 멤버의 userAccountId |

**Response**

```json
{
  "status": 200,
  "message": "ok",
  "data": null,
  "error": {}
}
```

**에러 코드**

| 코드 | HTTP | 상황 |
|------|------|------|
| STUDY_NOT_FOUND | 404 | 스터디 없음 |
| STUDY_OWNER_ONLY | 403 | 방장이 아님 |
| STUDY_NOT_MEMBER | 403 | 대상이 멤버가 아님 |

---

## 5. 알림 (Notice)

### 5.1 알림 목록 조회

```
GET /user-accounts/me/notices
```

**인증**: 필요
**권한**: 인증된 사용자

**Response**

```json
{
  "status": 200,
  "message": "ok",
  "data": {
    "notices": [
      {
        "noticeId": 1,
        "category": "STUDY_INVITATION_STATUS",
        "isRead": false,
        "createdAt": "2026-03-03T10:01:00",
        "content": {
          "studyName": "알고리즘 스터디",
          "userId": "jinus7949",
          "userCode": "396056",
          "status": "PENDING"
        }
      },
      {
        "noticeId": 2,
        "category": "STUDY_APPLICATION_STATUS",
        "isRead": false,
        "createdAt": "2026-03-03T10:05:00",
        "content": {
          "studyName": "알고리즘 스터디",
          "status": "PENDING"
        }
      }
    ]
  },
  "error": {}
}
```

**NoticeCategory별 content 구조**

| category | content 필드 |
|----------|-------------|
| STUDY_INVITATION_STATUS | `studyName`, `userId`(초대자 bjAccountId), `userCode`(초대자), `status` |
| STUDY_APPLICATION_STATUS | `studyName`, `status` |

---

### 5.2 알림 일괄 읽음 처리

```
PATCH /user-accounts/me/notices/read
```

**인증**: 필요
**권한**: 인증된 사용자 (자신의 알림만 처리 가능)

**Request Body**

```json
{
  "noticeIds": [1, 2, 3]
}
```

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| noticeIds | integer[] | ✅ | 읽음 처리할 알림 ID 목록 |

**Response**

```json
{
  "status": 200,
  "message": "ok",
  "data": null,
  "error": {}
}
```

**에러 코드**

| 코드 | HTTP | 상황 |
|------|------|------|
| NOTICE_NOT_FOR_ME | 403 | 목록 중 본인 알림이 아닌 것 포함 |

---

### 5.3 SSE 알림 스트림

```
GET /user-accounts/me/notices/stream
```

**인증**: 필요
**권한**: 인증된 사용자

**Response**: `text/event-stream`

```
data: connected

data: {"noticeId": 3, "category": "STUDY_INVITATION_STATUS", "content": {...}}

data: {"noticeId": 4, "category": "STUDY_APPLICATION_STATUS", "content": {...}}
```

**구현 참고**: 단일 프로세스에서 `asyncio.Queue` 기반 in-memory pub/sub. 클라이언트가 연결을 끊으면 자동으로 disconnect 처리됨. 멀티 워커 환경에서는 Redis pub/sub 전환 필요.

---

## 6. 스터디 문제

### 6.1 전원 문제 할당

```
POST /studies/{study_id}/problems/all
```

**인증**: 필요
**권한**: 방장(OWNER)

**Path Parameters**

| 파라미터 | 타입 | 설명 |
|---------|------|------|
| study_id | integer | 스터디 ID |

**Request Body**

```json
{
  "problemId": 1000,
  "targetDate": "2026-03-15"
}
```

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| problemId | integer | ✅ | 백준 문제 번호 |
| targetDate | string | ✅ | 전원 동일 날짜 (`YYYY-MM-DD`) |

**Response**

```json
{
  "status": 200,
  "message": "ok",
  "data": null,
  "error": {}
}
```

**동작**: 스터디 전체 멤버에게 동일 날짜로 `study_problem_member` 레코드 생성.

**에러 코드**

| 코드 | HTTP | 상황 |
|------|------|------|
| STUDY_NOT_FOUND | 404 | 스터디 없음 |
| STUDY_OWNER_ONLY | 403 | 방장이 아님 |

---

### 6.2 개인별 문제 할당

```
POST /studies/{study_id}/problems
```

**인증**: 필요
**권한**: 방장(OWNER)

**Path Parameters**

| 파라미터 | 타입 | 설명 |
|---------|------|------|
| study_id | integer | 스터디 ID |

**Request Body**

```json
{
  "problemId": 1001,
  "assignments": [
    {"userAccountId": 544, "targetDate": "2026-03-15"},
    {"userAccountId": 546, "targetDate": "2026-03-16"}
  ]
}
```

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| problemId | integer | ✅ | 백준 문제 번호 |
| assignments | array | ✅ | 멤버별 할당 목록 |
| assignments[].userAccountId | integer | ✅ | 할당할 멤버 ID |
| assignments[].targetDate | string | ✅ | 해당 멤버의 풀어야 하는 날짜 (`YYYY-MM-DD`) |

**Response**

```json
{
  "status": 200,
  "message": "ok",
  "data": null,
  "error": {}
}
```

**동작**: `assignments` 배열의 각 항목마다 `study_problem_member` 레코드를 개별 생성. 멤버마다 날짜 독립 지정 가능.

**에러 코드**

| 코드 | HTTP | 상황 |
|------|------|------|
| STUDY_NOT_FOUND | 404 | 스터디 없음 |
| STUDY_OWNER_ONLY | 403 | 방장이 아님 |
| STUDY_PROBLEM_INVALID_TARGETS | 400 | assignments에 스터디 멤버가 아닌 ID 포함 |

---

### 6.3 문제 할당 삭제

```
DELETE /studies/{study_id}/problems/{study_problem_id}
```

**인증**: 필요
**권한**: 방장(OWNER)

**Path Parameters**

| 파라미터 | 타입 | 설명 |
|---------|------|------|
| study_id | integer | 스터디 ID |
| study_problem_id | integer | 스터디 문제 ID |

**Response**

```json
{
  "status": 200,
  "message": "ok",
  "data": null,
  "error": {}
}
```

**에러 코드**

| 코드 | HTTP | 상황 |
|------|------|------|
| STUDY_PROBLEM_NOT_FOUND | 404 | 문제 없음 |
| STUDY_OWNER_ONLY | 403 | 방장이 아님 |

---

### 6.4 스터디 문제 조회 (월별)

```
GET /studies/{study_id}/problems
```

**인증**: 필요
**권한**: 스터디 멤버

**Path Parameters**

| 파라미터 | 타입 | 설명 |
|---------|------|------|
| study_id | integer | 스터디 ID |

**Query Parameters**

| 파라미터 | 타입 | 필수 | 설명 |
|---------|------|------|------|
| year | integer | ✅ | 조회 연도 |
| month | integer | ✅ | 조회 월 |

**Response**

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
                "solveDate": "2026-03-03"
              },
              {
                "userAccountId": 546,
                "bjAccountId": "naem",
                "userCode": "208346",
                "solved": false,
                "solveDate": null
              }
            ],
            "status": "in_progress"
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
      }
    ]
  },
  "error": {}
}
```

**응답 필드**

| 필드 | 설명 |
|------|------|
| items | 날짜별 그룹화된 배열 |
| items[].targetDate | 날짜 (`YYYY-MM-DD`) |
| items[].problems | 해당 날짜에 할당된 문제 목록 |
| problems[].status | `solved` (전원 풀었음) \| `will_solve` (아무도 안 풀었음) \| `in_progress` (일부만 풀었음) |
| solveInfo[].solved | 풀이 여부 |
| solveInfo[].solveDate | 풀이 날짜 (`YYYY-MM-DD`) \| `null` |

**에러 코드**

| 코드 | HTTP | 상황 |
|------|------|------|
| STUDY_NOT_FOUND | 404 | 스터디 없음 |
| STUDY_NOT_MEMBER | 403 | 멤버가 아님 |

---

### 6.5 스터디 문제 추천

```
GET /studies/{study_id}/recommend-problems
```

**인증**: 필요
**권한**: 스터디 멤버

**Path Parameters**

| 파라미터 | 타입 | 설명 |
|---------|------|------|
| study_id | integer | 스터디 ID |

**Query Parameters**

| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|---------|------|------|--------|------|
| target_user_account_id | integer | ❌ | null | 추천 기준 멤버 (생략 시 본인 기준) |
| recommend_all_unsolved | boolean | ❌ | false | `true`이면 스터디 전원이 아직 안 푼 문제만 추천 |
| count | integer | ❌ | 3 | 추천 문제 수 |

**Response**

```json
{
  "status": 200,
  "message": "ok",
  "data": {
    "problems": [
      {
        "problemId": 1234,
        "title": "두 수의 합",
        "tier": 5,
        "studyMemberSolveInfo": [
          {
            "userAccountId": 544,
            "bjAccountId": "jinus7949",
            "solved": true
          },
          {
            "userAccountId": 546,
            "bjAccountId": "naem",
            "solved": false
          }
        ]
      }
    ]
  },
  "error": {}
}
```

| 필드 | 설명 |
|------|------|
| studyMemberSolveInfo | 스터디 멤버별 해당 문제 풀이 여부 |

**에러 코드**

| 코드 | HTTP | 상황 |
|------|------|------|
| STUDY_NOT_FOUND | 404 | 스터디 없음 |
| STUDY_NOT_MEMBER | 403 | 멤버가 아님 |

---

## 에러 코드 전체 목록

| 에러 코드 | HTTP | 설명 |
|----------|------|------|
| USER_CODE_EXHAUSTED | 500 | 유저 코드 고갈 (100회 재시도 실패) |
| BJ_ACCOUNT_NOT_LINKED | 400 | 백준 계정 미연동 유저의 스터디 참여 시도 |
| STUDY_NOT_FOUND | 404 | 스터디 없음 |
| STUDY_NAME_ALREADY_TAKEN | 400 | 스터디명 중복 |
| STUDY_FULL | 400 | 스터디 정원 초과 |
| STUDY_ALREADY_MEMBER | 400 | 이미 스터디 멤버 |
| STUDY_NOT_MEMBER | 403 | 스터디 멤버가 아님 |
| STUDY_OWNER_ONLY | 403 | 방장 권한 필요 |
| INVITATION_NOT_FOUND | 404 | 초대 없음 |
| INVITATION_ALREADY_SENT | 400 | 이미 PENDING 초대 존재 |
| INVITATION_ALREADY_RESPONDED | 400 | 이미 처리된 초대 |
| INVITATION_NOT_FOR_ME | 403 | 내 초대가 아님 |
| APPLICATION_NOT_FOUND | 404 | 신청 없음 |
| APPLICATION_ALREADY_SENT | 400 | PENDING 신청 이미 존재 |
| APPLICATION_ALREADY_RESPONDED | 400 | 이미 처리된 신청 |
| STUDY_PROBLEM_NOT_FOUND | 404 | 스터디 문제 없음 |
| STUDY_PROBLEM_INVALID_TARGETS | 400 | assignments에 스터디 멤버가 아닌 ID 포함 |
| NOTICE_NOT_FOUND | 404 | 알림 없음 |
| NOTICE_NOT_FOR_ME | 403 | 내 알림이 아님 |
