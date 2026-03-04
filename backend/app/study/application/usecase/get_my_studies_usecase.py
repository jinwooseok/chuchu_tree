from app.common.domain.vo.identifiers import UserAccountId
from app.core.database import transactional
from app.study.application.command.study_command import GetMyStudiesCommand
from app.study.application.query.study_query import MyStudyItemQuery
from app.study.domain.repository.study_repository import StudyRepository
from app.study.domain.repository.user_search_repository import UserSearchRepository


class GetMyStudiesUsecase:
    def __init__(
        self,
        study_repository: StudyRepository,
        user_search_repository: UserSearchRepository,
    ):
        self.study_repository = study_repository
        self.user_search_repository = user_search_repository

    @transactional(readonly=True)
    async def execute(self, command: GetMyStudiesCommand) -> list[MyStudyItemQuery]:
        studies = await self.study_repository.find_by_member_user_account_id(
            UserAccountId(command.requester_user_account_id)
        )

        owner_ids = list({s.owner_user_account_id.value for s in studies})
        owner_infos = await self.user_search_repository.find_by_user_account_ids(owner_ids)
        owner_map = {u.user_account_id: u for u in owner_infos}

        return [
            MyStudyItemQuery(
                study_id=s.study_id.value,
                study_name=s.study_name,
                owner_user_account_id=s.owner_user_account_id.value,
                owner_bj_account_id=owner_map[s.owner_user_account_id.value].bj_account_id
                if s.owner_user_account_id.value in owner_map else "",
                owner_user_code=owner_map[s.owner_user_account_id.value].user_code
                if s.owner_user_account_id.value in owner_map else "",
                description=s.description,
                max_members=s.max_members,
                member_count=s.active_member_count(),
                created_at=s.created_at.isoformat(),
            )
            for s in studies
        ]
