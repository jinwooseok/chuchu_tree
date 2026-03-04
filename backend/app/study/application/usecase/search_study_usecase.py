from app.core.database import transactional
from app.study.application.command.study_command import SearchStudyCommand
from app.study.application.query.study_query import StudySearchItemQuery
from app.study.domain.repository.study_repository import StudyRepository


class SearchStudyUsecase:
    def __init__(self, study_repository: StudyRepository):
        self.study_repository = study_repository

    @transactional(readonly=True)
    async def execute(self, command: SearchStudyCommand) -> list[StudySearchItemQuery]:
        results = await self.study_repository.search(command.keyword, command.limit)
        return [
            StudySearchItemQuery(
                study_id=r.study_id,
                study_name=r.study_name,
                owner_bj_account_id=r.owner_bj_account_id,
                owner_user_code=r.owner_user_code,
                member_count=r.member_count,
            )
            for r in results
        ]
