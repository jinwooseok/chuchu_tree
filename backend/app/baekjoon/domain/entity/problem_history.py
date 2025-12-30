from dataclasses import dataclass
from datetime import datetime

from app.common.domain.vo.identifiers import BaekjoonAccountId, ProblemId

@dataclass
class ProblemHistory:
    """Entity - 문제 해결 히스토리"""
    problem_history_id: int|None
    bj_account_id: BaekjoonAccountId
    problem_id: ProblemId
    solved_at: datetime
    created_at: datetime
    
    @staticmethod
    def create(
        bj_account_id: BaekjoonAccountId,
        problem_id: ProblemId,
        solved_at: datetime
    ) -> 'ProblemHistory':
        return ProblemHistory(
            problem_history_id=None,
            bj_account_id=bj_account_id,
            problem_id=problem_id,
            solved_at=solved_at,
            created_at=datetime.now()
        )