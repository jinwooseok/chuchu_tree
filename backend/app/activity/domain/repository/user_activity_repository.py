from abc import ABC, abstractmethod
from datetime import date

from app.activity.domain.entity.user_activity import UserActivity
from app.activity.domain.entity.user_problem_status import UserProblemStatus
from app.common.domain.vo.identifiers import UserAccountId


class UserActivityRepository(ABC):
    """Repository 인터페이스"""

    @abstractmethod
    async def find_will_solve_problems_by_date(
        self,
        user_id: 'UserAccountId',
        target_date: date
    ) -> list[UserProblemStatus]:
        pass

    @abstractmethod
    async def find_problem_records_by_date(
        self,
        user_id: 'UserAccountId',
        target_date: date
    ) -> list[UserProblemStatus]:
        pass

    @abstractmethod
    async def find_monthly_problem_records(
        self,
        user_id: UserAccountId,
        year: int,
        month: int
    ) -> list[UserProblemStatus]:
        """월간 푼 문제 기록 조회"""
        pass

    @abstractmethod
    async def find_monthly_will_solve_problems(
        self,
        user_id: UserAccountId,
        year: int,
        month: int
    ) -> list[UserProblemStatus]:
        """월간 풀 예정 문제 조회"""
        pass

    @abstractmethod
    async def save_all_will_solve_problems(self, statuses: list[UserProblemStatus]) -> None:
        pass

    @abstractmethod
    async def save_all_problem_records(self, statuses: list[UserProblemStatus]) -> None:
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
    ) -> list[UserProblemStatus]:
        """특정 문제 ID들의 solved 상태 조회 (모든 날짜)"""
        pass

    @abstractmethod
    async def find_will_solve_problems_by_problem_ids(
        self,
        user_id: UserAccountId,
        problem_ids: list[int]
    ) -> list[UserProblemStatus]:
        """특정 문제 ID들의 will_solve 상태 조회 (모든 날짜)"""
        pass

    @abstractmethod
    async def find_problem_record_by_problem_id(
        self,
        user_id: UserAccountId,
        problem_id: int
    ) -> UserProblemStatus | None:
        """특정 문제 ID의 solved 상태 조회 (단일)"""
        pass

    @abstractmethod
    async def find_will_solve_problem_by_problem_id(
        self,
        user_id: UserAccountId,
        problem_id: int
    ) -> UserProblemStatus | None:
        """특정 문제 ID의 will_solve 상태 조회 (단일)"""
        pass

    @abstractmethod
    async def delete_all_by_user_account_id(self, user_account_id: UserAccountId) -> None:
        """사용자와 연관된 모든 활동 데이터 삭제 (Hard Delete)"""
        pass

    @abstractmethod
    async def save_problem_status(self, status: UserProblemStatus) -> None:
        """단일 UserProblemStatus 저장"""
        pass

    @abstractmethod
    async def count_solved_by_date(
        self,
        user_id: UserAccountId,
        bj_account_id: str,
        target_date: date
    ) -> int:
        """특정 날짜의 활성 SOLVED 레코드 수 조회"""
        pass
