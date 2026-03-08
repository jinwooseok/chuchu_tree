from abc import ABC, abstractmethod

from app.common.domain.vo.identifiers import StudyApplicationId, StudyId, UserAccountId
from app.study.domain.entity.study_application import StudyApplication


class StudyApplicationRepository(ABC):
    @abstractmethod
    async def insert(self, application: StudyApplication) -> StudyApplication:
        ...

    @abstractmethod
    async def find_by_id(self, application_id: StudyApplicationId) -> StudyApplication | None:
        ...

    @abstractmethod
    async def find_pending_by_study(self, study_id: StudyId) -> list[StudyApplication]:
        ...

    @abstractmethod
    async def find_pending_by_applicant(self, applicant_id: UserAccountId) -> list[StudyApplication]:
        ...

    @abstractmethod
    async def find_by_study_and_applicant(
        self, study_id: StudyId, applicant_id: UserAccountId
    ) -> StudyApplication | None:
        ...

    @abstractmethod
    async def update(self, application: StudyApplication) -> StudyApplication:
        ...

    @abstractmethod
    async def soft_delete(self, application: StudyApplication) -> None:
        ...

    @abstractmethod
    async def delete_all_by_user_account_id(self, user_account_id: UserAccountId) -> None:
        ...
