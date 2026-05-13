from dataclasses import dataclass
from datetime import datetime

from app.common.domain.enums import ApplicationStatus
from app.common.domain.vo.identifiers import StudyApplicationId, StudyId, UserAccountId


@dataclass
class StudyApplication:
    application_id: StudyApplicationId | None
    study_id: StudyId
    applicant_user_account_id: UserAccountId
    status: ApplicationStatus
    message: str | None
    responded_at: datetime | None
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None

    @classmethod
    def create(
        cls,
        study_id: StudyId,
        applicant_user_account_id: UserAccountId,
        message: str | None = None,
    ) -> "StudyApplication":
        now = datetime.now()
        return cls(
            application_id=None,
            study_id=study_id,
            applicant_user_account_id=applicant_user_account_id,
            status=ApplicationStatus.PENDING,
            message=message,
            responded_at=None,
            created_at=now,
            updated_at=now,
            deleted_at=None,
        )

    def accept(self) -> None:
        self.status = ApplicationStatus.ACCEPTED
        self.responded_at = datetime.now()
        self.updated_at = datetime.now()

    def reject(self) -> None:
        self.status = ApplicationStatus.REJECTED
        self.responded_at = datetime.now()
        self.updated_at = datetime.now()
