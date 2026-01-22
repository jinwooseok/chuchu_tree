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
    async def find_problem_records_by_date(
        self,
        user_id: 'UserAccountId',
        target_date: date
    ) -> list['ProblemRecord']:
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
    async def save_all_problem_records(
        self, 
        problem_records: list[ProblemRecord]
    ) -> None:
        pass
    
    @abstractmethod
    async def find_only_tag_custom_by_user_account_id(self, user_account_id: UserAccountId) -> UserActivity:
        pass
    
    @abstractmethod
    async def find_by_user_account_id(self, user_account_id: UserAccountId) -> UserActivity:
        pass
    
    @abstractmethod
    async def save_tag_custom(self, activity: UserActivity):
        pass    
    
    @abstractmethod
    async def find_only_banned_problem_by_user_account_id(self, user_account_id: UserAccountId) -> UserActivity:
        pass
    
    @abstractmethod
    async def save_problem_banned_record(self, activity: UserActivity):
        pass

    @abstractmethod
    async def find_problem_records_by_problem_ids(
        self,
        user_id: UserAccountId,
        problem_ids: list[int]
    ) -> list[ProblemRecord]:
        """특정 문제 ID들의 problem_record 조회 (모든 날짜)"""
        pass

    @abstractmethod
    async def find_will_solve_problems_by_problem_ids(
        self,
        user_id: UserAccountId,
        problem_ids: list[int]
    ) -> list[WillSolveProblem]:
        """특정 문제 ID들의 will_solve_problem 조회 (모든 날짜)"""
        pass

    @abstractmethod
    async def delete_all_by_user_account_id(self, user_account_id: UserAccountId) -> None:
        """
        사용자와 연관된 모든 활동 데이터 삭제 (Hard Delete)
        - tag_custom
        - problem_record
        - will_solve_problem
        - problem_banned_record
        """
        pass
    
    @abstractmethod
    async def save_problem_record(
        self, 
        problem_record: ProblemRecord
    ) -> None:
        """
        save_problem_record의 Docstring
        
        :param problem_record: 문제 기록 엔티티
        :type problem_record: ProblemRecord
        """
        pass