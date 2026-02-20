from dataclasses import dataclass
from datetime import date, datetime
from enum import Enum


class RecordType(str, Enum):
    """날짜별 기록 유형"""
    WILL_SOLVE = "WILL_SOLVE"
    SOLVED = "SOLVED"


@dataclass
class ProblemDateRecord:
    """Entity - 날짜별 문제 기록 (problem_date_record 테이블과 1:1 대응)"""
    problem_date_record_id: int | None
    user_problem_status_id: int | None
    marked_date: date
    record_type: RecordType
    display_order: int
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None

    @staticmethod
    def create(
        user_problem_status_id: int | None,
        marked_date: date,
        record_type: RecordType,
        display_order: int = 0
    ) -> 'ProblemDateRecord':
        now = datetime.now()
        return ProblemDateRecord(
            problem_date_record_id=None,
            user_problem_status_id=user_problem_status_id,
            marked_date=marked_date,
            record_type=record_type,
            display_order=display_order,
            created_at=now,
            updated_at=now,
            deleted_at=None
        )

    def delete(self) -> None:
        """소프트 삭제"""
        self.display_order = -1
        self.updated_at = datetime.now()
        self.deleted_at = datetime.now()

    def restore(self) -> None:
        """복구"""
        self.deleted_at = None
        self.updated_at = datetime.now()

    def change_order(self, new_order: int) -> None:
        """순서 변경"""
        if self.display_order != new_order:
            self.display_order = new_order
            self.updated_at = datetime.now()
