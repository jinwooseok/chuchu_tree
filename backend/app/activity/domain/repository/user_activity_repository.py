from abc import ABC, abstractmethod
from datetime import date

from app.activity.domain.entity.problem_record import ProblemRecord
from app.activity.domain.entity.tag_customization import TagCustomization
from app.activity.domain.entity.user_activity import UserActivity
from app.activity.domain.entity.will_solve_problem import WillSolveProblem
from app.common.domain.vo.identifiers import UserAccountId

class UserActivityRepository(ABC):
    """Repository 인터페이스"""

    @abstractmethod
    async def find_will_solve_problems_by_date(
        self,
        user_id: 'UserAccountId',
        target_date: date
    ) -> list['WillSolveProblem']:
        pass

    @abstractmethod
    async def find_monthly_problem_records(
        self,
        user_id: UserAccountId,
        year: int,
        month: int
    ) -> list[ProblemRecord]:
        """월간 푼 문제 기록 조회"""
        pass

    @abstractmethod
    async def find_monthly_will_solve_problems(
        self,
        user_id: UserAccountId,
        year: int,
        month: int
    ) -> list[WillSolveProblem]:
        """월간 풀 예정 문제 조회"""
        pass
    
    @abstractmethod
    async def save_all_will_solve_problems(self, will_solve_problems: list['WillSolveProblem']) -> None:
        pass
    
    @abstractmethod
    async def find_only_tag_custom_by_user_account_id(user_account_id: UserAccountId) -> UserActivity:
        pass
    
    @abstractmethod
    async def find_by_user_account_id(user_account_id: UserAccountId) -> UserActivity:
        pass
    
    @abstractmethod
    async def save_tag_custom(activity: UserActivity):
        pass    