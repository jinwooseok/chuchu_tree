from app.common.domain.vo.identifiers import StudyId, StudyInvitationId, UserAccountId
from app.core.database import transactional
from app.core.error_codes import ErrorCode
from app.core.exception import APIException
from app.study.application.command.study_command import CancelStudyInvitationCommand
from app.study.domain.repository.study_invitation_repository import StudyInvitationRepository
from app.study.domain.repository.study_repository import StudyRepository


class CancelStudyInvitationUsecase:
    def __init__(
        self,
        study_repository: StudyRepository,
        invitation_repository: StudyInvitationRepository,
    ):
        self.study_repository = study_repository
        self.invitation_repository = invitation_repository

    @transactional
    async def execute(self, command: CancelStudyInvitationCommand) -> None:
        study = await self.study_repository.find_by_id(StudyId(command.study_id))
        if study is None:
            raise APIException(ErrorCode.STUDY_NOT_FOUND)
        if not study.is_owner(UserAccountId(command.requester_user_account_id)):
            raise APIException(ErrorCode.STUDY_OWNER_ONLY)
        invitation = await self.invitation_repository.find_by_id(StudyInvitationId(command.invitation_id))
        if invitation is None:
            raise APIException(ErrorCode.INVITATION_NOT_FOUND)
        await self.invitation_repository.soft_delete(invitation)
