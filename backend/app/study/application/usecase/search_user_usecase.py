from app.common.domain.gateway.storage_gateway import StorageGateway
from app.core.database import transactional
from app.study.application.command.study_command import SearchUserCommand
from app.study.application.query.user_search_query import UserSearchItemQuery
from app.study.domain.repository.user_search_repository import UserSearchRepository

DEFAULT_PROFILE_IMAGE_PATH = "default-user-image.svg"


class SearchUserUsecase:
    def __init__(self, user_search_repository: UserSearchRepository, storage_gateway: StorageGateway):
        self.user_search_repository = user_search_repository
        self.storage_gateway = storage_gateway

    @transactional(readonly=True)
    async def execute(self, command: SearchUserCommand) -> list[UserSearchItemQuery]:
        results = await self.user_search_repository.search_by_keyword(command.keyword, command.limit)
        queries = []
        for r in results:
            profile_image = r.profile_image or DEFAULT_PROFILE_IMAGE_PATH
            profile_image_url = await self.storage_gateway.generate_presigned_url(profile_image)
            queries.append(
                UserSearchItemQuery(
                    user_account_id=r.user_account_id,
                    bj_account_id=r.bj_account_id,
                    user_code=r.user_code,
                    profile_image_url=profile_image_url,
                )
            )
        return queries
