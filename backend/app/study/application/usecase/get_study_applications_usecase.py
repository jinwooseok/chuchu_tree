from app.common.domain.gateway.storage_gateway import StorageGateway
from app.common.domain.vo.identifiers import StudyId, UserAccountId
from app.core.database import transactional
from app.core.error_codes import ErrorCode
from app.core.exception import APIException
from app.study.application.command.study_command import GetStudyApplicationsCommand
from app.study.application.query.application_query import ApplicationQuery
from app.study.domain.repository.study_application_repository import StudyApplicationRepository
from app.study.domain.repository.study_repository import StudyRepository
from app.study.domain.repository.user_search_repository import UserSearchRepository

DEFAULT_PROFILE_IMAGE_PATH = "default-user-image.svg"


class GetStudyApplicationsUsecase:
    def __init__(
        self,
        study_repository: StudyRepository,
        application_repository: StudyApplicationRepository,
        user_search_repository: UserSearchRepository,
        storage_gateway: StorageGateway,
    ):
        self.study_repository = study_repository
        self.application_repository = application_repository
        self.user_search_repository = user_search_repository
        self.storage_gateway = storage_gateway

    @transactional(readonly=True)
    async def execute(self, command: GetStudyApplicationsCommand) -> list[ApplicationQuery]:
        study = await self.study_repository.find_by_id(StudyId(command.study_id))
        if study is None:
            raise APIException(ErrorCode.STUDY_NOT_FOUND)
        if not study.is_member(UserAccountId(command.requester_user_account_id)):
            raise APIException(ErrorCode.STUDY_NOT_MEMBER)

        applications = await self.application_repository.find_pending_by_study(study.study_id)
        applicant_ids = [a.applicant_user_account_id.value for a in applications]
        user_infos = await self.user_search_repository.find_by_user_account_ids(applicant_ids)
        user_info_map = {u.user_account_id: u for u in user_infos}

        result = []
        for a in applications:
            info = user_info_map.get(a.applicant_user_account_id.value)
            profile_image = (info.profile_image if info else None) or DEFAULT_PROFILE_IMAGE_PATH
            profile_image_url = await self.storage_gateway.generate_presigned_url(profile_image)
            result.append(
                ApplicationQuery(
                    application_id=a.application_id.value,
                    study_id=a.study_id.value,
                    applicant_user_account_id=a.applicant_user_account_id.value,
                    applicant_bj_account_id=info.bj_account_id if info else "",
                    applicant_user_code=info.user_code if info else "",
                    status=a.status.value,
                    message=a.message,
                    created_at=a.created_at.isoformat(),
                    applicant_profile_image_url=profile_image_url,
                )
            )
        return result
