from dataclasses import dataclass
from datetime import date, datetime

from app.common.domain.vo.identifiers import ProblemId, UserAccountId


@dataclass
class WillSolveProblem:
    """Entity - 풀 문제"""
    will_solve_problem_id: int|None
    user_account_id: UserAccountId
    problem_id: ProblemId
    solved: bool
    marked_date: date
    order: int
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
            solved=False,
            order=0,
            marked_date=marked_date,
            created_at=now,
            updated_at=now,
            deleted_at=None
        )
    
    def delete(self) -> None:
        """마킹 해제"""
        self.order = -1
        self.updated_at = datetime.now()
        self.deleted_at = datetime.now()
    
    def restore(self) -> None:
        """삭제되었던 문제를 다시 추가할 경우 복구"""
        self.deleted_at = None
        self.updated_at = datetime.now()
    
    def change_order(self, new_order: int) -> None:
        """순서 변경: 순서가 실제로 다를 때만 업데이트 수행"""
        if self.order != new_order:
            self.order = new_order
            self.updated_at = datetime.now()