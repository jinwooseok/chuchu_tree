# is_synced 필드 추가 + Token Whitelist & RTR

**작성일**: 2026-02-20

---

## 요약

두 가지 기능을 구현했습니다:
1. **is_synced**: AccountLink에 배치 동기화 여부 추적 필드 추가. 프론트엔드에서 동기화를 권장할 수 있도록 함.
2. **Token Whitelist + RTR**: Refresh Token을 Redis 화이트리스트로 관리하고, Refresh Token Rotation 전략을 적용하여 보안 강화.

---

## Feature 1: is_synced

### 개요

백준 계정 연동 시 문제 풀이 이력이 있는 경우 배치 동기화가 필요합니다. `is_synced` 필드를 통해 동기화 상태를 추적하고, 프론트엔드에서 사용자에게 동기화를 안내할 수 있습니다.

### 상태 흐름

```
백준 계정 연동 (problem_history > 0) -> is_synced = False
백준 계정 연동 (problem_history == 0) -> is_synced = True (동기화할 문제 없음)
배치 동기화 완료                      -> is_synced = True
백준 계정 변경 (새 link 생성)          -> 새 link의 is_synced = False/True (문제 수에 따라)
```

### 변경 파일

| 파일 | 변경 내용 |
|------|----------|
| `app/user/domain/entity/account_link.py` | `is_synced` 필드 + `mark_as_synced()` 메서드 추가 |
| `app/user/infra/model/account_link.py` | `is_synced` DB 컬럼 추가 (`Boolean, default=False`) |
| `app/user/infra/mapper/account_link_mapper.py` | `is_synced` 양방향 매핑 추가 |
| `alembic/versions/a1b2c3d4e5f6_add_is_synced_to_account_link.py` | 마이그레이션 (down_revision: `3f0a6a57a553`) |
| `app/baekjoon/domain/event/link_bj_account_payload.py` | `problem_count` 필드 추가 |
| `app/user/application/command/link_bj_account_command.py` | `problem_count` 필드 추가 |
| `app/baekjoon/application/usecase/link_bj_account_usecase.py` | 기존/신규 BJ 계정의 problem 수 계산 후 이벤트에 전달 |
| `app/user/domain/entity/user_account.py` | `link_baekjoon_account()`에 `problem_count` 파라미터 추가, `is_synced=(problem_count == 0)` |
| `app/user/application/command/mark_synced_command.py` | **신규** - `BATCH_SYNC_COMPLETED` 이벤트 커맨드 |
| `app/user/application/service/user_account_application_service.py` | `mark_account_link_synced()` 이벤트 핸들러 + `link_baekjoon_account()` problem_count 전달 + `get_user_account_info()` is_synced 반환 |
| `app/user/application/query/user_account_info_query.py` | `is_synced` 응답 필드 추가 |
| `app/activity/application/service/activity_application_service.py` | `batch_create_solved_problems()` 완료 시 `BATCH_SYNC_COMPLETED` 이벤트 발행 |

---

## Feature 2: Token Whitelist + RTR

### 개요

기존에는 Refresh Token이 stateless하게 관리되어, 토큰 탈취 시 만료 전까지 악용 가능했습니다.
Redis 화이트리스트 + RTR(Refresh Token Rotation)을 적용하여:
- RT는 1회 사용 후 폐기되고 새 RT 발급
- 사용된 RT의 재사용 시도 감지 -> 해당 유저의 전체 세션 종료
- 로그아웃/회원탈퇴 시 모든 RT 즉시 폐기

### Redis Key 설계

| Key 패턴 | 용도 | TTL |
|----------|------|-----|
| `rt:{user_id}:{jti}` | 활성 RT 화이트리스트 | 7일 |
| `rt:used:{jti}` | 사용된 RT 기록 (재사용 감지) | 7일 |

### RTR 흐름

```
1. POST /auth/token/refresh (refresh_token 쿠키)
2. decode refresh_token -> user_account_id, jti 추출
3. 재사용 감지: is_token_used(jti) -> 감지 시 revoke_all_user_tokens + TOKEN_REUSE_DETECTED 에러
4. 화이트리스트 확인: is_token_valid(user_id, jti) -> 없으면 INVALID_TOKEN 에러
5. 기존 RT 폐기: revoke_token + mark_as_used
6. 새 AT + RT 발급 (새 jti)
7. 새 RT 화이트리스트에 저장
8. 쿠키에 새 AT + RT 설정
```

### 변경 파일

| 파일 | 변경 내용 |
|------|----------|
| `app/common/domain/service/token_service.py` | `create_refresh_token()` 추상 메서드 추가 (jti 포함 RT 생성) |
| `app/common/infra/security/jwt_token_service.py` | `create_refresh_token()` 구현 (uuid4 jti, type: "refresh") |
| `app/common/domain/gateway/refresh_token_whitelist_gateway.py` | **신규** - Gateway 인터페이스 (`store_token`, `is_token_valid`, `revoke_token`, `mark_as_used`, `is_token_used`, `revoke_all_user_tokens`) |
| `app/common/infra/gateway/refresh_token_whitelist_gateway_impl.py` | **신규** - Redis 구현체 (CsrfTokenGatewayImpl 패턴 준용) |
| `app/common/application/service/auth_application_service.py` | `refresh_token_whitelist` 의존성 추가, `_create_and_set_tokens()` async 전환, `refresh_access_token()` RTR 로직 전체 구현, `logout()` user_account_id 받아 RT 전체 폐기, 회원탈퇴 시 RT 폐기 |
| `app/common/presentation/controller/auth_controller.py` | `logout()`에 `current_user.user_account_id` 전달 |
| `app/core/containers.py` | `refresh_token_whitelist_gateway` DI 등록, `auth_application_service`에 주입 |
| `app/core/error_codes.py` | `TOKEN_REUSE_DETECTED` 에러 코드 추가 |

---

## 추가된 테스트

### Feature 1: is_synced 테스트

| 파일 | 테스트 | 설명 |
|------|--------|------|
| `tests/unit/user/entity/test_account_link.py` | **신규 6개** | `create()` is_synced 기본값/True/False, `mark_as_synced()`, `mark_as_deleted()` |
| `tests/unit/user/entity/test_user_account.py` | **+3개** | `link_baekjoon_account()` problem_count에 따른 is_synced 설정 |
| `tests/unit/user/application/test_user_account_application_service.py` | **+7개** | link problem_count 전달, `mark_account_link_synced()` 핸들러, `get_user_account_info()` is_synced 반환 |

### Feature 2: Token Whitelist + RTR 테스트

| 파일 | 테스트 | 설명 |
|------|--------|------|
| `tests/unit/common/security/test_jwt_token_service.py` | **신규 6개** | `create_refresh_token()` 반환값/jti/type/유일성/만료, 기존 `create_token()` 회귀 테스트 |
| `tests/unit/common/gateway/test_refresh_token_whitelist_gateway.py` | **신규 12개** | `store_token`, `is_token_valid`, `revoke_token`, `mark_as_used`, `is_token_used`, `revoke_all_user_tokens`, Redis 에러 처리 |
| `tests/unit/common/application/test_auth_application_service.py` | **기존 테스트 수정 + 7개 추가** | `refresh_token_whitelist` 의존성 반영, RTR 정상 흐름, 재사용 감지, 화이트리스트 미존재, jti 없는 토큰, `logout()` RT 폐기, `_create_and_set_tokens()` 화이트리스트 저장 |

### 테스트 총계

- **신규 테스트**: 41개
- **수정된 기존 테스트**: 10개 (refresh_token_whitelist 의존성 추가)

---

## 검증 방법

### 1. is_synced

```bash
# Alembic 마이그레이션 적용
alembic upgrade head

# 검증 항목
# - 백준 계정 연동 (문제 있는 계정) -> AccountLink.is_synced = false
# - 백준 계정 연동 (문제 없는 계정) -> AccountLink.is_synced = true
# - POST /user-problems/problems/solved-problems/batch -> is_synced = true
# - GET /users/me -> is_synced 필드 노출
```

### 2. Token Whitelist + RTR

```bash
# 검증 항목
# - 소셜 로그인 후 Redis에서 rt:{user_id}:* 키 존재 확인
# - POST /auth/token/refresh -> 새 AT + RT 쿠키 발급, Redis 키 교체 확인
# - 동일 RT로 재요청 -> TOKEN_REUSE_DETECTED 에러 + 전체 RT 삭제
# - POST /auth/logout -> Redis에서 해당 유저 RT 전체 삭제
```

### 3. 유닛 테스트 실행

```bash
pytest tests/unit/user/entity/test_account_link.py \
       tests/unit/user/entity/test_user_account.py \
       tests/unit/common/security/test_jwt_token_service.py \
       tests/unit/common/gateway/test_refresh_token_whitelist_gateway.py \
       tests/unit/common/application/test_auth_application_service.py \
       tests/unit/user/application/test_user_account_application_service.py -v
```

### 4. API 수동 테스트 실행=

### 요약

### Baekjoon /me 도메인 - isSynced 필드 반영
- [ ] Case 1 - 동기화 완료된 유저의 /baekjoon/me 조회 시 isSynced=true
- [ ] Case 2 - 동기화 미완료 유저의 /baekjoon/me 조회 시 isSynced=false
- [ ] Case 3 - 동기화 완료한 후 연동 계정 변경 시 isSynced=false

---

## 테스트 상세

### Baekjoon /me 도메인 - isSynced 필드 반영

---

**Case 1 - 동기화 완료된 유저의 /baekjoon/me 조회 시 isSynced=true**

URL: `GET /api/v1/bj-accounts/me`

사전 조건: 백준 계정 연동 완료 + 배치 동기화 완료 (account_link.is_synced = true)

예상: 응답의 `userAccount` 객체에 `isSynced: true` 포함. 결과:

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
      "userAccountId": 365,
      "profileImageUrl": null,
      "target": {
        "targetId": 1,
        "targetCode": "DAILY",
        "targetDisplayName": "DAILY"
      },
      "registeredAt": "2026-02-15T14:12:34",
      "isSynced": true
    },
    "bjAccount": {
      "bjAccountId": "jinus7949",
```

---

**Case 2 - 동기화 미완료 유저의 /baekjoon/me 조회 시 isSynced=false**

URL: `GET /api/v1/bj-accounts/me`

사전 조건: 백준 계정 연동 직후 (배치 동기화 아직 미완료, account_link.is_synced = false)

예상: 응답의 `userAccount` 객체에 `isSynced: false` 포함. 결과:

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
      "userAccountId": 365,
      "profileImageUrl": null,
      "target": {
        "targetId": 1,
        "targetCode": "DAILY",
        "targetDisplayName": "DAILY"
      },
      "registeredAt": "2026-02-15T14:12:34",
      "isSynced": false
    },
    "bjAccount": {
      "bjAccountId": "jinus7949",
```

**Case 3 - 유저가 연동 계정을 변동한 후 /baekjoon/me 조회 시 isSynced=false**

URL: `GET /api/v1/bj-accounts/me`

사전 조건: 새로운 백준 계정 (happynj2697) 연동

예상: 응답의 `userAccount` 객체에 `isSynced: true` 포함. 결과:

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
      "userAccountId": 365,
      "profileImageUrl": null,
      "target": {
        "targetId": 1,
        "targetCode": "DAILY",
        "targetDisplayName": "DAILY"
      },
      "registeredAt": "2026-02-15T14:12:34",
      "isSynced": false
    },
    "bjAccount": {
      "bjAccountId": "happynj2697",
```