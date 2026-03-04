from app.common.domain.vo.identifiers import StudyId, UserAccountId
from app.core.database import transactional
from app.core.error_codes import ErrorCode
from app.core.exception import APIException
from app.study.application.command.study_command import GetStudyApplicationsCommand
from app.study.application.query.application_query import ApplicationQuery
from app.study.domain.repository.study_application_repository import StudyApplicationRepository
from app.study.domain.repository.study_repository import StudyRepository
from app.study.domain.repository.user_search_repository import UserSearchRepository


class GetStudyApplicationsUsecase:
    def __init__(
        self,
        study_repository: StudyRepository,
        application_repository: StudyApplicationRepository,
        user_search_repository: UserSearchRepository,
    ):
        self.study_repository = study_repository
        self.application_repository = application_repository
        self.user_search_repository = user_search_repository

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

        return [
            ApplicationQuery(
                application_id=a.application_id.value,
                study_id=a.study_id.value,
                applicant_user_account_id=a.applicant_user_account_id.value,
                applicant_bj_account_id=user_info_map.get(a.applicant_user_account_id.value, None) and user_info_map[a.applicant_user_account_id.value].bj_account_id or "",
                applicant_user_code=user_info_map.get(a.applicant_user_account_id.value, None) and user_info_map[a.applicant_user_account_id.value].user_code or "",
                status=a.status.value,
                message=a.message,
                created_at=a.created_at.isoformat(),
            )
            for a in applications
        ]
