from dataclasses import dataclass
from datetime import date, datetime

from app.common.domain.vo.identifiers import ProblemId, UserAccountId


@dataclass
class WillSolveProblem:
    """Entity - 풀 문제"""
    will_solve_problem_id: int|None
    user_account_id: UserAccountId
    problem_id: ProblemId
    marked: bool
    marked_date: date
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime|None = None
    
    @staticmethod
    def create(
        user_account_id: 'UserAccountId',
        problem_id: 'ProblemId',
        marked_date: date
    ) -> 'WillSolveProblem':
        now = datetime.now()
        return WillSolveProblem(
            will_solve_problem_id=None,
            user_account_id=user_account_id,
            problem_id=problem_id,
            marked=True,
            marked_date=marked_date,
            created_at=now,
            updated_at=now,
            deleted_at=None
        )
    
    def unmark(self) -> None:
        """마킹 해제"""
        self.marked = False
        self.updated_at = datetime.now()