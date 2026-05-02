from app.core.database import transactional
from app.study.application.command.study_command import ValidateStudyNameCommand
from app.study.application.query.study_query import NameAvailableQuery
from app.study.domain.repository.study_repository import StudyRepository


class ValidateStudyNameUsecase:
    def __init__(self, study_repository: StudyRepository):
        self.study_repository = study_repository

    @transactional(readonly=True)
    async def execute(self, command: ValidateStudyNameCommand) -> NameAvailableQuery:
        taken = await self.study_repository.is_name_taken(command.name)
        return NameAvailableQuery(available=not taken)
