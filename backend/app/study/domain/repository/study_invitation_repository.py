from abc import ABC, abstractmethod

from app.common.domain.vo.identifiers import StudyId, StudyInvitationId, UserAccountId
from app.study.domain.entity.study_invitation import StudyInvitation


class StudyInvitationRepository(ABC):
    @abstractmethod
    async def insert(self, invitation: StudyInvitation) -> StudyInvitation:
        ...

    @abstractmethod
    async def find_by_id(self, invitation_id: StudyInvitationId) -> StudyInvitation | None:
        ...

    @abstractmethod
    async def find_pending_by_invitee(self, invitee_id: UserAccountId) -> list[StudyInvitation]:
        ...

    @abstractmethod
    async def find_by_study_and_invitee(
        self, study_id: StudyId, invitee_id: UserAccountId
    ) -> StudyInvitation | None:
        ...

    @abstractmethod
    async def find_pending_by_study(self, study_id: StudyId) -> list[StudyInvitation]:
        ...

    @abstractmethod
    async def update(self, invitation: StudyInvitation) -> StudyInvitation:
        ...

    @abstractmethod
    async def soft_delete(self, invitation: StudyInvitation) -> None:
        ...

    @abstractmethod
    async def delete_all_by_user_account_id(self, user_account_id: UserAccountId) -> None:
        ...
