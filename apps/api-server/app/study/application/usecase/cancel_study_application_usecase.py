from app.common.domain.vo.identifiers import StudyId, UserAccountId
from app.core.database import transactional
from app.core.error_codes import ErrorCode
from app.core.exception import APIException
from app.study.application.command.study_command import CancelStudyApplicationCommand
from app.study.domain.repository.study_application_repository import StudyApplicationRepository
from app.study.domain.repository.study_repository import StudyRepository


class CancelStudyApplicationUsecase:
    def __init__(
        self,
        study_repository: StudyRepository,
        application_repository: StudyApplicationRepository,
    ):
        self.study_repository = study_repository
        self.application_repository = application_repository

    @transactional
    async def execute(self, command: CancelStudyApplicationCommand) -> None:
        study = await self.study_repository.find_by_id(StudyId(command.study_id))
        if study is None:
            raise APIException(ErrorCode.STUDY_NOT_FOUND)

        applicant_id = UserAccountId(command.requester_user_account_id)
        application = await self.application_repository.find_by_study_and_applicant(
            study.study_id, applicant_id
        )
        if application is None:
            raise APIException(ErrorCode.APPLICATION_NOT_FOUND)

        await self.application_repository.soft_delete(application)
