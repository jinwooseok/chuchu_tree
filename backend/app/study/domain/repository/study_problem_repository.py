from abc import ABC, abstractmethod
from datetime import date

from app.common.domain.vo.identifiers import StudyId, StudyProblemId, UserAccountId
from app.study.domain.entity.study_problem import StudyProblem, StudyProblemMember


class StudyProblemRepository(ABC):
    @abstractmethod
    async def insert(self, study_problem: StudyProblem, members: list[StudyProblemMember]) -> StudyProblem:
        ...

    @abstractmethod
    async def find_by_id(self, study_problem_id: StudyProblemId) -> StudyProblem | None:
        ...

    @abstractmethod
    async def find_by_study_and_date_range(
        self, study_id: StudyId, start: date, end: date
    ) -> list[StudyProblem]:
        ...

    @abstractmethod
    async def find_by_user_and_date_range(
        self, user_account_id: UserAccountId, start: date, end: date
    ) -> list[StudyProblem]:
        ...

    @abstractmethod
    async def soft_delete(self, problem: StudyProblem) -> None:
        ...

    @abstractmethod
    async def delete_members_by_user(self, user_account_id: int) -> None:
        """Soft delete all study_problem_member rows for a given user (탈퇴 시)"""
        ...

    @abstractmethod
    async def delete_members_by_user_hard(self, user_account_id: int) -> None:
        """Hard delete all study_problem_member rows for a given user"""
        ...
