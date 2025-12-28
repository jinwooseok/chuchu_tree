from abc import ABC, abstractmethod
from datetime import date

from app.activity.domain.entity.user_activity import UserActivity
from app.activity.domain.entity.will_solve_problem import WillSolveProblem
from app.common.domain.vo.identifiers import UserAccountId

class UserActivityRepository(ABC):
    """Repository 인터페이스"""
    
    @abstractmethod
    async def save(self, activity: UserActivity) -> UserActivity:
        pass
    
    @abstractmethod
    async def find_by_user_id(self, user_id: 'UserAccountId') -> UserActivity|None:
        pass
    
    @abstractmethod
    async def find_will_solve_problems_by_date(
        self,
        user_id: 'UserAccountId',
        target_date: date
    ) -> list['WillSolveProblem']:
        pass