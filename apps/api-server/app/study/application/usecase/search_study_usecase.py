from app.common.domain.gateway.storage_gateway import StorageGateway
from app.core.database import transactional
from app.study.application.command.study_command import SearchStudyCommand
from app.study.application.query.study_query import StudySearchItemQuery
from app.study.domain.repository.study_repository import StudyRepository

DEFAULT_PROFILE_IMAGE_PATH = "default-user-image.svg"


class SearchStudyUsecase:
    def __init__(self, study_repository: StudyRepository, storage_gateway: StorageGateway):
        self.study_repository = study_repository
        self.storage_gateway = storage_gateway

    @transactional(readonly=True)
    async def execute(self, command: SearchStudyCommand) -> list[StudySearchItemQuery]:
        results = await self.study_repository.search(command.keyword, command.limit)
        queries = []
        for r in results:
            profile_image = r.owner_profile_image or DEFAULT_PROFILE_IMAGE_PATH
            owner_profile_image_url = await self.storage_gateway.generate_presigned_url(profile_image)
            queries.append(
                StudySearchItemQuery(
                    study_id=r.study_id,
                    study_name=r.study_name,
                    owner_bj_account_id=r.owner_bj_account_id,
                    owner_user_code=r.owner_user_code,
                    member_count=r.member_count,
                    owner_profile_image_url=owner_profile_image_url,
                )
            )
        return queries
