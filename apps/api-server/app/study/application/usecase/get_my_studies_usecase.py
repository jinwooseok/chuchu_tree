from app.common.domain.gateway.storage_gateway import StorageGateway
from app.common.domain.vo.identifiers import UserAccountId
from app.core.database import transactional
from app.study.application.command.study_command import GetMyStudiesCommand
from app.study.application.query.study_query import MyStudyItemQuery
from app.study.domain.repository.study_repository import StudyRepository
from app.study.domain.repository.user_search_repository import UserSearchRepository

DEFAULT_PROFILE_IMAGE_PATH = "default-user-image.svg"


class GetMyStudiesUsecase:
    def __init__(
        self,
        study_repository: StudyRepository,
        user_search_repository: UserSearchRepository,
        storage_gateway: StorageGateway,
    ):
        self.study_repository = study_repository
        self.user_search_repository = user_search_repository
        self.storage_gateway = storage_gateway

    @transactional(readonly=True)
    async def execute(self, command: GetMyStudiesCommand) -> list[MyStudyItemQuery]:
        studies = await self.study_repository.find_by_member_user_account_id(
            UserAccountId(command.requester_user_account_id)
        )

        owner_ids = list({s.owner_user_account_id.value for s in studies})
        owner_infos = await self.user_search_repository.find_by_user_account_ids(owner_ids)
        owner_map = {u.user_account_id: u for u in owner_infos}

        result = []
        for s in studies:
            owner = owner_map.get(s.owner_user_account_id.value)
            profile_image = (owner.profile_image if owner else None) or DEFAULT_PROFILE_IMAGE_PATH
            owner_profile_image_url = await self.storage_gateway.generate_presigned_url(profile_image)
            result.append(
                MyStudyItemQuery(
                    study_id=s.study_id.value,
                    study_name=s.study_name,
                    owner_user_account_id=s.owner_user_account_id.value,
                    owner_bj_account_id=owner.bj_account_id if owner else "",
                    owner_user_code=owner.user_code if owner else "",
                    description=s.description,
                    max_members=s.max_members,
                    member_count=s.active_member_count(),
                    created_at=s.created_at.isoformat(),
                    owner_profile_image_url=owner_profile_image_url,
                )
            )
        return result
