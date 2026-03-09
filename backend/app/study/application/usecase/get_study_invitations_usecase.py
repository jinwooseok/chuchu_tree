from app.common.domain.gateway.storage_gateway import StorageGateway
from app.common.domain.vo.identifiers import StudyId, UserAccountId
from app.core.database import transactional
from app.core.error_codes import ErrorCode
from app.core.exception import APIException
from app.study.application.command.study_command import GetStudyInvitationsCommand
from app.study.application.query.study_query import StudyPendingInvitationQuery
from app.study.domain.repository.study_invitation_repository import StudyInvitationRepository
from app.study.domain.repository.study_repository import StudyRepository
from app.study.domain.repository.user_search_repository import UserSearchRepository

DEFAULT_PROFILE_IMAGE_PATH = "default-user-image.svg"


class GetStudyInvitationsUsecase:
    def __init__(
        self,
        study_repository: StudyRepository,
        invitation_repository: StudyInvitationRepository,
        user_search_repository: UserSearchRepository,
        storage_gateway: StorageGateway,
    ):
        self.study_repository = study_repository
        self.invitation_repository = invitation_repository
        self.user_search_repository = user_search_repository
        self.storage_gateway = storage_gateway

    @transactional(readonly=True)
    async def execute(self, command: GetStudyInvitationsCommand) -> list[StudyPendingInvitationQuery]:
        study = await self.study_repository.find_by_id(StudyId(command.study_id))
        if study is None:
            raise APIException(ErrorCode.STUDY_NOT_FOUND)
        if not study.is_member(UserAccountId(command.requester_user_account_id)):
            raise APIException(ErrorCode.STUDY_NOT_MEMBER)

        invitations = await self.invitation_repository.find_pending_by_study(StudyId(command.study_id))

        invitee_ids = list({inv.invitee_user_account_id.value for inv in invitations})
        invitee_map = {
            u.user_account_id: u
            for u in await self.user_search_repository.find_by_user_account_ids(invitee_ids)
        }

        result = []
        for inv in invitations:
            invitee = invitee_map.get(inv.invitee_user_account_id.value)
            profile_image = (invitee.profile_image if invitee else None) or DEFAULT_PROFILE_IMAGE_PATH
            profile_image_url = await self.storage_gateway.generate_presigned_url(profile_image)
            result.append(
                StudyPendingInvitationQuery(
                    invitation_id=inv.invitation_id.value,
                    invitee_user_account_id=inv.invitee_user_account_id.value,
                    invitee_bj_account_id=invitee.bj_account_id if invitee else "",
                    invitee_user_code=invitee.user_code if invitee else "",
                    created_at=inv.created_at.isoformat(),
                    profile_image_url=profile_image_url,
                )
            )
        return result
