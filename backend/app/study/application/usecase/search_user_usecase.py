from app.core.database import transactional
from app.study.application.command.study_command import SearchUserCommand
from app.study.application.query.user_search_query import UserSearchItemQuery
from app.study.domain.repository.user_search_repository import UserSearchRepository


class SearchUserUsecase:
    def __init__(self, user_search_repository: UserSearchRepository):
        self.user_search_repository = user_search_repository

    @transactional(readonly=True)
    async def execute(self, command: SearchUserCommand) -> list[UserSearchItemQuery]:
        results = await self.user_search_repository.search_by_keyword(command.keyword, command.limit)
        return [
            UserSearchItemQuery(
                user_account_id=r.user_account_id,
                bj_account_id=r.bj_account_id,
                user_code=r.user_code,
            )
            for r in results
        ]
