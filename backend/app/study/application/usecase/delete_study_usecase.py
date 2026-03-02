from app.common.domain.vo.identifiers import StudyId, UserAccountId
from app.core.database import transactional
from app.core.error_codes import ErrorCode
from app.core.exception import APIException
from app.study.application.command.study_command import DeleteStudyCommand
from app.study.domain.repository.study_repository import StudyRepository


class DeleteStudyUsecase:
    def __init__(self, study_repository: StudyRepository):
        self.study_repository = study_repository

    @transactional
    async def execute(self, command: DeleteStudyCommand) -> None:
        study = await self.study_repository.find_by_id(StudyId(command.study_id))
        if study is None:
            raise APIException(ErrorCode.STUDY_NOT_FOUND)
        if not study.is_owner(UserAccountId(command.requester_user_account_id)):
            raise APIException(ErrorCode.STUDY_OWNER_ONLY)
        await self.study_repository.soft_delete(study)
