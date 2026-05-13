# Activity 도메인 엔티티 리팩토링 (구조 정규화)

**작성일**: 2026-02-20

---

## 요약

Activity 도메인의 엔티티 구조를 DB 테이블 구조와 일치하도록 리팩토링했습니다.

기존에는 DB가 이미 `user_problem_status` + `problem_date_record`로 정규화되어 있었음에도, 도메인 엔티티는 구 구조인 `WillSolveProblem`, `ProblemRecord`, `ProblemBannedRecord` 3개로 남아 있었습니다. 이번 PR에서 도메인 엔티티를 DB 구조에 맞게 재정의하여 ID 불일치, 매퍼 복잡도, 개념 불일치 문제를 해결했습니다.

---

## 배경

| 구분 | 기존 | 변경 후 |
|------|------|---------|
| DB 테이블 | `user_problem_status`, `problem_date_record` | 동일 (변경 없음) |
| 도메인 엔티티 | `WillSolveProblem`, `ProblemRecord`, `ProblemBannedRecord` (3개) | `UserProblemStatus`, `ProblemDateRecord` (2개) |
| 매퍼 | 3 엔티티 ↔ 2 테이블 복잡 변환 | 1:1 직접 매핑 |

### 왜 기존에 DB와 도메인이 달랐는가

초기 설계에서는 DB도 도메인 엔티티와 동일하게 `will_solve_problem`, `problem_record`, `problem_banned_record` 3개 테이블이었습니다. 이후 DB를 `user_problem_status` + `problem_date_record` 구조로 정규화하는 마이그레이션을 진행했는데, 당시 영향 범위를 최소화하기 위해 **DB 레이어만 변경하고 도메인 엔티티는 그대로 유지**했습니다. 매퍼에서 구조 불일치를 흡수하는 방식으로 임시 처리했고, 이번 PR에서 그 기술 부채를 해소합니다.

### 도메인 엔티티임에도 DB 구조에 맞추는 이유

DDD에서 도메인 엔티티는 원칙적으로 DB 구조와 독립적이어야 합니다. 그러나 이 경우는 오히려 DB 정규화 후 도메인이 그 개념을 따라가지 못한 상황입니다.

`user_problem_status` + `problem_date_record` 구조는 단순히 DB 최적화가 아니라, **"한 문제에 대해 유저는 하나의 상태를 가지며, 그 상태에 날짜별 이력이 쌓인다"** 는 비즈니스 개념을 더 정확히 표현합니다. 기존 3개 엔티티 구조는 오히려 이 개념을 왜곡하고 있었으므로, DB 구조가 비즈니스 개념에 더 가깝다고 판단하여 도메인을 맞추었습니다.

**기존 구조의 문제점**
- `will_solve_problem_id` 필드가 실제로는 `problem_date_record_id`를 담고 있어 이름과 실제가 불일치
- 3개 엔티티 ↔ 2개 테이블 간 변환 로직이 복잡해 유지보수 어려움
- "문제별 단일 상태 + 날짜 이력"이라는 비즈니스 개념을 도메인이 표현하지 못함

### `will_solve_problems` 등을 computed property로 처리한 이유

`UserActivity`의 내부 저장소는 `problem_statuses: list[UserProblemStatus]` 하나로 통합되었지만, 외부에서 접근하는 인터페이스는 기존과 동일하게 유지했습니다.

```python
# 내부 저장 방식은 바뀌었지만, 외부 인터페이스는 그대로
activity.will_solve_problems  # → problem_statuses를 필터링한 결과
activity.banned_problems
activity.solved_problems
```

이렇게 함으로써 **Application 레이어의 변경을 최소화**할 수 있었습니다. Application Service는 여전히 `activity.will_solve_problems`로 접근하면 되고, 내부 구현이 단일 리스트로 바뀐 사실을 알 필요가 없습니다. 도메인 엔티티가 내부 표현 방식의 변화를 캡슐화하여 상위 레이어로의 파급을 막는 전형적인 패턴입니다.

---

## 주요 변경 사항

### 1. 신규 도메인 엔티티 생성

**`app/activity/domain/entity/problem_date_record.py`** (신규)

날짜별 기록을 표현하는 도메인 엔티티. `RecordType` enum (`WILL_SOLVE` / `SOLVED`)도 이 파일에 정의하여 도메인 계층이 인프라에 의존하는 구조를 제거.

```python
class RecordType(str, Enum):
    WILL_SOLVE = "WILL_SOLVE"
    SOLVED = "SOLVED"

@dataclass
class ProblemDateRecord:
    problem_date_record_id: int | None
    user_problem_status_id: int | None
    marked_date: date
    record_type: RecordType
    display_order: int
    ...
    def delete(self) -> None   # soft delete
    def restore(self) -> None
```

**`app/activity/domain/entity/user_problem_status.py`** (신규)

문제별 마스터 엔티티. 기존 3개 엔티티(`WillSolveProblem`, `ProblemRecord`, `ProblemBannedRecord`)를 통합.

```python
@dataclass
class UserProblemStatus:
    user_problem_status_id: int | None
    user_account_id: UserAccountId
    problem_id: ProblemId
    banned_yn: bool
    solved_yn: bool
    date_records: list[ProblemDateRecord]
    ...
    @staticmethod def create_will_solve(...) -> 'UserProblemStatus'
    @staticmethod def create_solved(...) -> 'UserProblemStatus'
    @staticmethod def create_banned(...) -> 'UserProblemStatus'
    def is_banned(self) -> bool
    def is_will_solve(self) -> bool
    def is_solved(self) -> bool
```

**`app/activity/infra/mapper/user_problem_status_mapper.py`** (신규)

기존 `problem_record_mapper.py`를 대체하는 단순화된 1:1 매퍼.

---

### 2. 수정된 파일

| 파일 | 변경 내용 |
|------|----------|
| `app/activity/domain/entity/user_activity.py` | `problem_statuses: list[UserProblemStatus]` 단일 리스트로 통합. `will_solve_problems`, `banned_problems`, `solved_problems`는 computed property로 제공 |
| `app/activity/infra/mapper/user_activity_mapper.py` | `UserProblemStatusMapper` 기반으로 단순화 |
| `app/activity/infra/model/problem_date_record.py` | `RecordType` enum을 도메인에서 import하도록 변경 (역방향 의존성 제거) |
| `app/activity/domain/repository/user_activity_repository.py` | 반환 타입을 `UserProblemStatus`로 통일, `save_problem_status()` 추가 |
| `app/activity/infra/repository/user_activity_repository_impl.py` | `_save_status_with_date_records()` 통합 저장 메서드, 반환 타입 전환 |
| `app/activity/application/service/activity_application_service.py` | `UserProblemStatus.create_will_solve/solved/banned()` 팩토리 사용으로 전환 |
| `app/user/infra/model/user_account.py` | 구 테이블에 대한 레거시 relationship 제거 (`problem_records`, `banned_problems`, `will_solve_problems`) |
| `app/core/database_models.py` | 구 인프라 모델 import 제거 (`ProblemRecordModel`, `ProblemBannedRecordModel`, `WillSolveProblemModel`) |
| `app/baekjoon/infra/repository/problem_history_repository_impl.py` | LEFT JOIN 대상을 `ProblemRecordModel` → `UserProblemStatusModel`로 교체 |
| `app/user/infra/repository/user_account_repository_impl.py` | 유저 삭제 시 구 테이블 3개 삭제 → `UserProblemStatusModel` 단일 삭제 (CASCADE) |

---

### 3. 삭제된 파일

| 파일 | 이유 |
|------|------|
| `app/activity/domain/entity/will_solve_problem.py` | `UserProblemStatus`로 통합 |
| `app/activity/domain/entity/problem_record.py` | `UserProblemStatus`로 통합 |
| `app/activity/domain/entity/problem_banned_record.py` | `UserProblemStatus`로 통합 |
| `app/activity/infra/mapper/problem_record_mapper.py` | `UserProblemStatusMapper`로 대체 |

---

## 수정된 테스트

| 파일 | 변경 내용 |
|------|----------|
| `tests/unit/activity/entity/test_user_activity.py` | 구 엔티티 import 제거, 새 API 기준으로 assertion 수정 |
| `tests/unit/activity/application/test_activity_application_service.py` | `WillSolveProblem.create()` → `UserProblemStatus.create_will_solve()` 전환 |

**테스트 결과**

```bash
pytest tests/unit/activity/ -v
# 52 passed
pytest tests/unit/
# 270 passed
```

---

## 검증 방법

```bash
# Activity 도메인 단위 테스트
pytest tests/unit/activity/ -v

# 전체 단위 테스트
pytest tests/unit/