from dataclasses import dataclass, field
from datetime import date, datetime

from app.activity.domain.entity.problem_date_record import ProblemDateRecord, RecordType
from app.common.domain.vo.identifiers import ProblemId, TagId, UserAccountId


@dataclass
class UserProblemStatus:
    """Entity - 문제별 사용자 상태 (user_problem_status 테이블과 1:1 대응)

    하나의 (user, bj_account, problem) 쌍에 대한 마스터 레코드.
    - banned_yn=True: 차단된 문제 (date_records 없음, bj_account_id=None)
    - solved_yn=True: 해결된 문제 (date_records에 SOLVED 레코드)
    - 둘 다 False: 풀 예정 문제 (date_records에 WILL_SOLVE 레코드)
    """
    user_problem_status_id: int | None
    user_account_id: UserAccountId
    problem_id: ProblemId
    banned_yn: bool
    solved_yn: bool
    representative_tag_id: TagId | None
    memo_title: str | None
    content: str | None
    date_records: list[ProblemDateRecord] = field(default_factory=list)
    bj_account_id: str | None = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    deleted_at: datetime | None = None

    # ===== 팩토리 메서드 =====

    @staticmethod
    def create_will_solve(
        user_account_id: UserAccountId,
        problem_id: ProblemId,
        marked_date: date,
        display_order: int = 0,
        bj_account_id: str | None = None
    ) -> 'UserProblemStatus':
        """풀 예정 문제 생성"""
        now = datetime.now()
        date_record = ProblemDateRecord.create(
            user_problem_status_id=None,
            marked_date=marked_date,
            record_type=RecordType.WILL_SOLVE,
            display_order=display_order
        )
        return UserProblemStatus(
            user_problem_status_id=None,
            user_account_id=user_account_id,
            problem_id=problem_id,
            banned_yn=False,
            solved_yn=False,
            representative_tag_id=None,
            memo_title=None,
            content=None,
            date_records=[date_record],
            bj_account_id=bj_account_id,
            created_at=now,
            updated_at=now,
            deleted_at=None
        )

    @staticmethod
    def create_solved(
        user_account_id: UserAccountId,
        problem_id: ProblemId,
        marked_date: date,
        display_order: int = 0,
        bj_account_id: str | None = None
    ) -> 'UserProblemStatus':
        """해결된 문제 생성"""
        now = datetime.now()
        date_record = ProblemDateRecord.create(
            user_problem_status_id=None,
            marked_date=marked_date,
            record_type=RecordType.SOLVED,
            display_order=display_order
        )
        return UserProblemStatus(
            user_problem_status_id=None,
            user_account_id=user_account_id,
            problem_id=problem_id,
            banned_yn=False,
            solved_yn=True,
            representative_tag_id=None,
            memo_title=None,
            content=None,
            date_records=[date_record],
            bj_account_id=bj_account_id,
            created_at=now,
            updated_at=now,
            deleted_at=None
        )

    @staticmethod
    def create_banned(
        user_account_id: UserAccountId,
        problem_id: ProblemId
    ) -> 'UserProblemStatus':
        """차단된 문제 생성 (date_records 없음, bj_account_id=None: 유저 레벨)"""
        now = datetime.now()
        return UserProblemStatus(
            user_problem_status_id=None,
            user_account_id=user_account_id,
            problem_id=problem_id,
            banned_yn=True,
            solved_yn=False,
            representative_tag_id=None,
            memo_title=None,
            content=None,
            date_records=[],
            bj_account_id=None,
            created_at=now,
            updated_at=now,
            deleted_at=None
        )

    # ===== 상태 판별 =====

    def is_banned(self) -> bool:
        return self.banned_yn and self.deleted_at is None

    def is_solved(self) -> bool:
        return self.solved_yn and not self.banned_yn

    def is_will_solve(self) -> bool:
        return not self.banned_yn and not self.solved_yn and self._has_active_record(RecordType.WILL_SOLVE)

    # ===== 편의 프로퍼티 (단일 date_record 컨텍스트용) =====

    @property
    def marked_date(self) -> date | None:
        """활성 date_record의 날짜 (날짜 필터 쿼리 결과에서 사용)"""
        active = self._get_active_date_records()
        return active[0].marked_date if active else None

    @property
    def order(self) -> int:
        """활성 date_record의 순서"""
        active = self._get_active_date_records()
        return active[0].display_order if active else 0

    # ===== 위임 메서드 (서비스 호환성) =====

    def change_order(self, new_order: int) -> None:
        """첫 번째 활성 date_record의 순서 변경"""
        active = self._get_active_date_records()
        if active:
            active[0].change_order(new_order)
        self.updated_at = datetime.now()

    def delete(self) -> None:
        """모든 활성 date_record 소프트 삭제"""
        for dr in self.date_records:
            if dr.deleted_at is None:
                dr.delete()
        self.updated_at = datetime.now()

    def restore(self) -> None:
        """첫 번째 date_record 복구"""
        active_deleted = [dr for dr in self.date_records if dr.deleted_at is not None]
        if active_deleted:
            active_deleted[-1].restore()
        self.updated_at = datetime.now()

    def set_representative_tag(self, tag_id: TagId | None) -> None:
        """대표 태그 설정"""
        self.representative_tag_id = tag_id
        self.updated_at = datetime.now()

    # ===== 내부 헬퍼 =====

    def _get_active_date_records(self) -> list[ProblemDateRecord]:
        return [dr for dr in self.date_records if dr.deleted_at is None]

    def _has_active_record(self, record_type: RecordType) -> bool:
        return any(
            dr.deleted_at is None and dr.record_type == record_type
            for dr in self.date_records
        )
