from dataclasses import dataclass
from datetime import date, datetime

from app.common.domain.vo.identifiers import ProblemId, UserAccountId


@dataclass
class ProblemRecord:
    """Entity - 문제 기록"""
    problem_record_id: int|None
    user_account_id: UserAccountId
    problem_id: ProblemId
    marked_date: date
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime|None = None
    
    @staticmethod
    def create(
        user_account_id: UserAccountId,
        problem_id: ProblemId,
        marked_date: date
    ) -> 'ProblemRecord':
        now = datetime.now()
        return ProblemRecord(
            problem_record_id=None,
            user_account_id=user_account_id,
            problem_id=problem_id,
            marked_date=marked_date,
            created_at=now,
            updated_at=now,
            deleted_at=None
        )