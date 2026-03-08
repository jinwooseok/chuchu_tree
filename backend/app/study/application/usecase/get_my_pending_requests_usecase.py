from app.common.domain.gateway.storage_gateway import StorageGateway
from app.common.domain.vo.identifiers import UserAccountId
from app.core.database import transactional
from app.study.application.command.study_command import GetMyPendingRequestsCommand
from app.study.application.query.application_query import MyApplicationQuery
from app.study.application.query.invitation_query import InvitationQuery
from app.study.domain.repository.study_application_repository import StudyApplicationRepository
from app.study.domain.repository.study_invitation_repository import StudyInvitationRepository
from app.study.domain.repository.study_repository import StudyRepository
from app.study.domain.repository.user_search_repository import UserSearchRepository

DEFAULT_PROFILE_IMAGE_PATH = "default-user-image.svg"


class GetMyPendingRequestsUsecase:
    def __init__(
        self,
        invitation_repository: StudyInvitationRepository,
        application_repository: StudyApplicationRepository,
        study_repository: StudyRepository,
        user_search_repository: UserSearchRepository,
        storage_gateway: StorageGateway,
    ):
        self.invitation_repository = invitation_repository
        self.application_repository = application_repository
        self.study_repository = study_repository
        self.user_search_repository = user_search_repository
        self.storage_gateway = storage_gateway

    @transactional(readonly=True)
    async def execute(
        self, command: GetMyPendingRequestsCommand
    ) -> tuple[list[InvitationQuery], list[MyApplicationQuery]]:
        user_id = UserAccountId(command.requester_user_account_id)

        invitations = await self.invitation_repository.find_pending_by_invitee(user_id)
        applications = await self.application_repository.find_pending_by_applicant(user_id)

        # invitations: inviter 정보 bulk 조회
        inviter_ids = list({inv.inviter_user_account_id.value for inv in invitations})
        inviter_map = {
            u.user_account_id: u
            for u in await self.user_search_repository.find_by_user_account_ids(inviter_ids)
        }

        invitation_queries: list[InvitationQuery] = []
        for inv in invitations:
            study = await self.study_repository.find_by_id(inv.study_id)
            inviter = inviter_map.get(inv.inviter_user_account_id.value)
            profile_image = (inviter.profile_image if inviter else None) or DEFAULT_PROFILE_IMAGE_PATH
            profile_image_url = await self.storage_gateway.generate_presigned_url(profile_image)
            invitation_queries.append(
                InvitationQuery(
                    invitation_id=inv.invitation_id.value,
                    study_id=inv.study_id.value,
                    study_name=study.study_name if study else "",
                    inviter_user_account_id=inv.inviter_user_account_id.value,
                    inviter_bj_account_id=inviter.bj_account_id if inviter else "",
                    inviter_user_code=inviter.user_code if inviter else "",
                    status=inv.status.value,
                    created_at=inv.created_at.isoformat(),
                    inviter_profile_image_url=profile_image_url,
                )
            )

        # applications: study 정보 bulk 조회
        study_ids = list({app.study_id for app in applications})
        study_map = {}
        for study_id in study_ids:
            study = await self.study_repository.find_by_id(study_id)
            if study:
                study_map[study_id.value] = study

        # owner 정보 bulk 조회
        owner_ids = list({s.owner_user_account_id.value for s in study_map.values()})
        owner_map = {
            u.user_account_id: u
            for u in await self.user_search_repository.find_by_user_account_ids(owner_ids)
        }

        application_queries: list[MyApplicationQuery] = []
        for app in applications:
            study = study_map.get(app.study_id.value)
            owner = owner_map.get(study.owner_user_account_id.value) if study else None
            profile_image = (owner.profile_image if owner else None) or DEFAULT_PROFILE_IMAGE_PATH
            profile_image_url = await self.storage_gateway.generate_presigned_url(profile_image)
            application_queries.append(
                MyApplicationQuery(
                    application_id=app.application_id.value,
                    study_id=app.study_id.value,
                    study_name=study.study_name if study else "",
                    owner_user_account_id=study.owner_user_account_id.value if study else 0,
                    owner_bj_account_id=owner.bj_account_id if owner else "",
                    owner_user_code=owner.user_code if owner else "",
                    status=app.status.value,
                    message=app.message,
                    created_at=app.created_at.isoformat(),
                    owner_profile_image_url=profile_image_url,
                )
            )

        return invitation_queries, application_queries
