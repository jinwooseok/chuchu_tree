from app.common.domain.gateway.storage_gateway import StorageGateway
from app.common.domain.vo.identifiers import StudyId, UserAccountId
from app.core.database import transactional
from app.core.error_codes import ErrorCode
from app.core.exception import APIException
from app.study.application.command.study_command import GetStudyInvitationsCommand
from app.study.application.query.invitation_query import InvitationQuery
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
    async def execute(self, command: GetStudyInvitationsCommand) -> list[InvitationQuery]:
        study = await self.study_repository.find_by_id(StudyId(command.study_id))
        if study is None:
            raise APIException(ErrorCode.STUDY_NOT_FOUND)
        if not study.is_member(UserAccountId(command.requester_user_account_id)):
            raise APIException(ErrorCode.STUDY_NOT_MEMBER)

        invitations = await self.invitation_repository.find_pending_by_study(StudyId(command.study_id))

        inviter_ids = list({inv.inviter_user_account_id.value for inv in invitations})
        inviter_map = {
            u.user_account_id: u
            for u in await self.user_search_repository.find_by_user_account_ids(inviter_ids)
        }

        result = []
        for inv in invitations:
            inviter = inviter_map.get(inv.inviter_user_account_id.value)
            profile_image = (inviter.profile_image if inviter else None) or DEFAULT_PROFILE_IMAGE_PATH
            profile_image_url = await self.storage_gateway.generate_presigned_url(profile_image)
            result.append(
                InvitationQuery(
                    invitation_id=inv.invitation_id.value,
                    study_id=inv.study_id.value,
                    study_name=study.study_name,
                    inviter_user_account_id=inv.inviter_user_account_id.value,
                    inviter_bj_account_id=inviter.bj_account_id if inviter else "",
                    inviter_user_code=inviter.user_code if inviter else "",
                    status=inv.status.value,
                    created_at=inv.created_at.isoformat(),
                    inviter_profile_image_url=profile_image_url,
                )
            )
        return result
