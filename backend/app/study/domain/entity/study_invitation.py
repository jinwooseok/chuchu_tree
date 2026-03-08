from dataclasses import dataclass
from datetime import datetime

from app.common.domain.enums import InvitationStatus
from app.common.domain.vo.identifiers import StudyId, StudyInvitationId, UserAccountId


@dataclass
class StudyInvitation:
    invitation_id: StudyInvitationId | None
    study_id: StudyId
    invitee_user_account_id: UserAccountId
    inviter_user_account_id: UserAccountId
    status: InvitationStatus
    responded_at: datetime | None
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None

    @classmethod
    def create(
        cls,
        study_id: StudyId,
        invitee_user_account_id: UserAccountId,
        inviter_user_account_id: UserAccountId,
    ) -> "StudyInvitation":
        now = datetime.now()
        return cls(
            invitation_id=None,
            study_id=study_id,
            invitee_user_account_id=invitee_user_account_id,
            inviter_user_account_id=inviter_user_account_id,
            status=InvitationStatus.PENDING,
            responded_at=None,
            created_at=now,
            updated_at=now,
            deleted_at=None,
        )

    def accept(self) -> None:
        self.status = InvitationStatus.ACCEPTED
        self.responded_at = datetime.now()
        self.updated_at = datetime.now()

    def reject(self) -> None:
        self.status = InvitationStatus.REJECTED
        self.responded_at = datetime.now()
        self.updated_at = datetime.now()
