# API 테스트 계획서

## 개요

본 문서는 백엔드 API 38개에 대한 통합 테스트 계획을 정의합니다.

---

## 테스트 환경

- **테스트 프레임워크**: pytest + pytest-asyncio
- **HTTP 클라이언트**: httpx AsyncClient
- **DB 전략**: 테스트별 트랜잭션 자동 롤백
- **인증**: 테스트용 JWT 토큰 서비스 주입

---

## 우선순위 정의

| 우선순위 | 설명 | 기준 |
|---------|------|------|
| P0 | 필수 | 핵심 인증/사용자 기능 |
| P1 | 높음 | 주요 비즈니스 로직 |
| P2 | 중간 | 부가 기능 |
| P3 | 낮음 | 관리/통계 기능 |

---

## 도메인별 API 목록 및 테스트 계획

### 1. AUTH (인증) - P0

| API | 메서드 | 엔드포인트 | 테스트 시나리오 |
|-----|--------|-----------|----------------|
| 로그인 상태 확인 | GET | `/api/v1/auth/me` | ✅ 구현됨 |
| 로그아웃 | POST | `/api/v1/auth/logout` | - 성공 케이스<br>- 미인증 상태 호출 |

### 2. USER (사용자) - P0

| API | 메서드 | 엔드포인트 | 테스트 시나리오 |
|-----|--------|-----------|----------------|
| 사용자 정보 조회 | GET | `/api/v1/users/{user_account_id}` | - 성공 케이스<br>- 존재하지 않는 ID<br>- 권한 없는 조회 |
| 사용자 정보 수정 | PATCH | `/api/v1/users/{user_account_id}` | - 성공 케이스<br>- 유효성 검증 실패<br>- 권한 없는 수정 |

### 3. BAEKJOON (백준 연동) - P1

| API | 메서드 | 엔드포인트 | 테스트 시나리오 |
|-----|--------|-----------|----------------|
| 백준 아이디 연결 | POST | `/api/v1/users/{user_account_id}/baekjoon` | - 성공 케이스<br>- 이미 연결된 계정<br>- 존재하지 않는 백준 ID |
| 백준 아이디 해제 | DELETE | `/api/v1/users/{user_account_id}/baekjoon` | - 성공 케이스<br>- 연결되지 않은 상태 |
| 백준 정보 조회 | GET | `/api/v1/users/{user_account_id}/baekjoon` | - 성공 케이스<br>- 미연결 상태 |
| 푼 문제 목록 조회 | GET | `/api/v1/users/{user_account_id}/baekjoon/solved` | - 성공 케이스<br>- 페이지네이션<br>- 정렬 옵션 |
| 푼 문제 동기화 | POST | `/api/v1/users/{user_account_id}/baekjoon/sync` | - 성공 케이스<br>- 연결 안된 상태 |

### 4. TARGET (목표) - P1

| API | 메서드 | 엔드포인트 | 테스트 시나리오 |
|-----|--------|-----------|----------------|
| 목표 설정 | POST | `/api/v1/users/{user_account_id}/target` | - 성공 케이스<br>- 유효성 검증 실패<br>- 이미 존재하는 목표 |
| 목표 조회 | GET | `/api/v1/users/{user_account_id}/target` | - 성공 케이스<br>- 목표 없음 |
| 목표 수정 | PATCH | `/api/v1/users/{user_account_id}/target` | - 성공 케이스<br>- 유효성 검증 실패 |
| 목표 삭제 | DELETE | `/api/v1/users/{user_account_id}/target` | - 성공 케이스<br>- 목표 없음 |

### 5. ACTIVITY (활동 기록) - P2

| API | 메서드 | 엔드포인트 | 테스트 시나리오 |
|-----|--------|-----------|----------------|
| 활동 기록 조회 | GET | `/api/v1/users/{user_account_id}/activities` | - 성공 케이스<br>- 기간 필터<br>- 페이지네이션 |
| 일일 통계 조회 | GET | `/api/v1/users/{user_account_id}/activities/daily` | - 성공 케이스<br>- 날짜 범위 |
| 주간 통계 조회 | GET | `/api/v1/users/{user_account_id}/activities/weekly` | - 성공 케이스 |
| 월간 통계 조회 | GET | `/api/v1/users/{user_account_id}/activities/monthly` | - 성공 케이스 |
| 히트맵 데이터 조회 | GET | `/api/v1/users/{user_account_id}/activities/heatmap` | - 성공 케이스<br>- 연도 필터 |

### 6. PROBLEM (문제) - P1

| API | 메서드 | 엔드포인트 | 테스트 시나리오 |
|-----|--------|-----------|----------------|
| 문제 목록 조회 | GET | `/api/v1/problems` | - 성공 케이스<br>- 필터링<br>- 페이지네이션 |
| 문제 상세 조회 | GET | `/api/v1/problems/{problem_id}` | - 성공 케이스<br>- 존재하지 않는 ID |
| 문제 검색 | GET | `/api/v1/problems/search` | - 성공 케이스<br>- 검색어 없음 |

### 7. TAG (태그) - P2

| API | 메서드 | 엔드포인트 | 테스트 시나리오 |
|-----|--------|-----------|----------------|
| 태그 목록 조회 | GET | `/api/v1/tags` | - 성공 케이스 |
| 태그별 문제 수 조회 | GET | `/api/v1/tags/stats` | - 성공 케이스 |
| 사용자 태그 통계 | GET | `/api/v1/users/{user_account_id}/tags/stats` | - 성공 케이스<br>- 미연결 상태 |

### 8. RECOMMENDATION (추천) - P1

| API | 메서드 | 엔드포인트 | 테스트 시나리오 |
|-----|--------|-----------|----------------|
| 문제 추천 | GET | `/api/v1/users/{user_account_id}/recommendations` | - 성공 케이스<br>- 추천 옵션<br>- 백준 미연결 |
| 추천 히스토리 | GET | `/api/v1/users/{user_account_id}/recommendations/history` | - 성공 케이스<br>- 페이지네이션 |

---

## 구현 순서

### Phase 1: 핵심 인증 (P0)
1. ✅ `auth/me` - 완료
2. `auth/logout`
3. `users/{id}` GET/PATCH

### Phase 2: 핵심 비즈니스 (P1)
4. `baekjoon` 연동 API들
5. `target` 목표 API들
6. `problems` 문제 API들
7. `recommendations` 추천 API들

### Phase 3: 부가 기능 (P2)
8. `activities` 활동 기록 API들
9. `tags` 태그 API들

### Phase 4: 관리 기능 (P3)
10. 관리자 전용 API (해당시)

---

## 공통 테스트 시나리오

### 인증 관련
- [ ] 유효한 토큰으로 요청 - 성공
- [ ] 토큰 없이 요청 - 401 NO_LOGIN_STATUS
- [ ] 만료된 토큰으로 요청 - 401 EXPIRED_TOKEN
- [ ] 유효하지 않은 토큰으로 요청 - 401 INVALID_TOKEN

### 권한 관련
- [ ] 본인 리소스 접근 - 성공
- [ ] 타인 리소스 접근 - 403 FORBIDDEN

### 입력 검증
- [ ] 유효한 입력 - 성공
- [ ] 필수 필드 누락 - 422 VALIDATION_ERROR
- [ ] 잘못된 형식 - 422 VALIDATION_ERROR

### 리소스 조회
- [ ] 존재하는 리소스 - 성공
- [ ] 존재하지 않는 리소스 - 404 NOT_FOUND

---

## 테스트 실행 방법

```bash
# 전체 테스트 + 체크리스트 자동 업데이트
poetry run python scripts/run_tests.py

# 특정 도메인만 테스트
poetry run python scripts/run_tests.py auth

# 체크리스트만 업데이트 (테스트 실행 없이)
poetry run python scripts/run_tests.py --checklist

# pytest 직접 실행
poetry run pytest -v

# 특정 도메인 테스트
poetry run pytest tests/integration/auth/ -v

# 커버리지 포함
poetry run pytest --cov=app --cov-report=html
```

---

## 테스트 자동화

### 테스트 결과 문서화

테스트 실행 시 자동으로 체크리스트 문서가 생성/업데이트됩니다.

| 파일 | 설명 |
|-----|------|
| `docs/TEST_CHECKLIST.md` | 최신 테스트 결과 체크리스트 |
| `tests/reports/TEST_CHECKLIST_*.md` | 타임스탬프별 테스트 결과 히스토리 |
| `test_report.json` | pytest JSON 리포트 (임시) |

### 자동화 스크립트

| 스크립트 | 설명 |
|---------|------|
| `scripts/run_tests.py` | 테스트 실행 + 체크리스트 업데이트 통합 |
| `scripts/update_test_checklist.py` | JSON 결과 파싱 → 마크다운 체크리스트 생성 |

### 체크리스트 자동 생성 규칙

- 테스트 파일의 **docstring**이 체크리스트 항목으로 자동 추출됨
- 디렉토리 구조에서 **도메인 자동 감지** (`tests/integration/<domain>/`)
- 실패한 테스트에는 **오류 상세 정보** 포함

---

## 파일 구조

```
backend/
├── scripts/
│   ├── run_tests.py               # 테스트 + 체크리스트 통합 실행
│   └── update_test_checklist.py   # 체크리스트 자동 생성
├── docs/
│   ├── test_plan.md               # 테스트 계획서 (본 문서)
│   └── TEST_CHECKLIST.md          # 테스트 결과 체크리스트 (자동 생성)
├── tests/
│   ├── conftest.py                # 공통 fixtures
│   ├── reports/                   # 테스트 결과 히스토리
│   │   └── TEST_CHECKLIST_*.md
│   ├── unit/                      # 단위 테스트
│   │   └── (추후 확장)
│   └── integration/               # 통합 테스트
│       ├── auth/
│       │   ├── __init__.py
│       │   ├── test_auth_me.py    ✅
│       │   └── test_auth_logout.py
│       ├── user/
│       │   └── test_user_crud.py
│       ├── baekjoon/
│       │   └── test_baekjoon.py
│       ├── target/
│       │   └── test_target.py
│       ├── activity/
│       │   └── test_activity.py
│       ├── problem/
│       │   └── test_problem.py
│       ├── tag/
│       │   └── test_tag.py
│       └── recommendation/
│           └── test_recommendation.py
└── pytest.ini                     # pytest 설정 (JSON 리포트 포함)
```
