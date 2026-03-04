from app.common.domain.vo.identifiers import StudyId, UserAccountId
from app.core.database import transactional
from app.core.error_codes import ErrorCode
from app.core.exception import APIException
from app.study.application.command.study_command import UpdateStudyCommand
from app.study.domain.repository.study_repository import StudyRepository


class UpdateStudyUsecase:
    def __init__(self, study_repository: StudyRepository):
        self.study_repository = study_repository

    @transactional
    async def execute(self, command: UpdateStudyCommand) -> None:
        study = await self.study_repository.find_by_id(StudyId(command.study_id))
        if study is None:
            raise APIException(ErrorCode.STUDY_NOT_FOUND)
        if not study.is_owner(UserAccountId(command.requester_user_account_id)):
            raise APIException(ErrorCode.STUDY_OWNER_ONLY)

        from datetime import datetime
        if command.description is not None:
            study.description = command.description
        if command.max_members is not None:
            study.max_members = command.max_members
        study.updated_at = datetime.now()

        await self.study_repository.update(study)
