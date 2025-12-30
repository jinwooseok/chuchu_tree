from dataclasses import dataclass
from datetime import datetime

from app.common.domain.vo.identifiers import ProblemId, UserAccountId


@dataclass
class ProblemBannedRecord:
    """Entity - 문제 제외 기록"""
    problem_banned_record_id: int|None
    problem_id: ProblemId
    user_account_id: UserAccountId
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime|None = None
    
    @staticmethod
    def create(
        problem_id: ProblemId,
        user_account_id: UserAccountId
    ) -> 'ProblemBannedRecord':
        now = datetime.now()
        return ProblemBannedRecord(
            problem_banned_record_id=None,
            problem_id=problem_id,
            user_account_id=user_account_id,
            created_at=now,
            updated_at=now,
            deleted_at=None
        )