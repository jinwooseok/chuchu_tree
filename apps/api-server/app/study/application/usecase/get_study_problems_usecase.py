from calendar import monthrange
from datetime import date

from app.baekjoon.domain.event.get_problems_info_payload import GetProblemsInfoPayload
from app.common.domain.entity.domain_event import DomainEvent
from app.common.domain.service.event_publisher import DomainEventBus
from app.common.domain.vo.identifiers import BaekjoonAccountId, StudyId, UserAccountId
from app.core.database import transactional
from app.core.error_codes import ErrorCode
from app.core.exception import APIException
from app.problem.application.query.problems_info_query import ProblemsInfoQuery
from app.study.application.command.study_command import GetStudyProblemsCommand
from app.study.application.query.study_problem_query import (
    MemberSolveInfoQuery,
    StudyDayDataQuery,
    StudyProblemItemQuery,
    StudyProblemsQuery,
)
from app.study.domain.repository.study_problem_repository import StudyProblemRepository
from app.study.domain.repository.study_repository import StudyRepository
from app.study.domain.repository.user_search_repository import UserSearchRepository
from app.baekjoon.domain.repository.problem_history_repository import ProblemHistoryRepository


class GetStudyProblemsUsecase:
    def __init__(
        self,
        study_repository: StudyRepository,
        study_problem_repository: StudyProblemRepository,
        user_search_repository: UserSearchRepository,
        domain_event_bus: DomainEventBus,
        problem_history_repository: ProblemHistoryRepository,
    ):
        self.study_repository = study_repository
        self.study_problem_repository = study_problem_repository
        self.user_search_repository = user_search_repository
        self.domain_event_bus = domain_event_bus
        self.problem_history_repository = problem_history_repository

    @transactional(readonly=True)
    async def execute(self, command: GetStudyProblemsCommand) -> StudyProblemsQuery:
        study = await self.study_repository.find_by_id(StudyId(command.study_id))
        if study is None:
            raise APIException(ErrorCode.STUDY_NOT_FOUND)

        if not study.is_member(UserAccountId(command.requester_user_account_id)):
            raise APIException(ErrorCode.STUDY_NOT_MEMBER)

        # 월 범위 계산
        start = date(command.year, command.month, 1)
        last_day = monthrange(command.year, command.month)[1]
        end = date(command.year, command.month, last_day)

        study_problems = await self.study_problem_repository.find_by_study_and_date_range(
            StudyId(command.study_id), start, end
        )

        if not study_problems:
            return StudyProblemsQuery(study_data=[])

        # 문제 정보 bulk 조회 (domain event bus)
        problem_ids = list({sp.problem_id.value for sp in study_problems})
        problems_info = await self._fetch_problems_info(problem_ids)
        problem_info_map = problems_info.problems

        # 활성 멤버의 user_account_id → UserSearchResult 매핑
        all_user_ids = {
            m.user_account_id.value
            for sp in study_problems
            for m in sp.members
            if m.deleted_at is None
        }
        user_infos = await self.user_search_repository.find_by_user_account_ids(list(all_user_ids))
        user_map = {u.user_account_id: u for u in user_infos}

        # bj_account_id → solved problem_id set 조회
        bj_accounts = {u.bj_account_id for u in user_infos}
        solved_map: dict[str, set[int]] = {}
        for bj_id in bj_accounts:
            solved_ids = await self.problem_history_repository.find_solved_ids_by_bj_account_id(BaekjoonAccountId(bj_id))
            solved_map[bj_id] = set(solved_ids)

        # (target_date, study_problem_id) → StudyProblemItemQuery 누적 빌드
        item_map: dict[tuple[str, int], StudyProblemItemQuery] = {}
        date_order: list[str] = []
        date_items: dict[str, list[tuple[str, int]]] = {}

        for sp in study_problems:
            problem_info = problem_info_map.get(sp.problem_id.value)
            active_members = [m for m in sp.members if m.deleted_at is None]

            for member in active_members:
                date_str = member.target_date.isoformat()
                key = (date_str, sp.study_problem_id.value)

                if key not in item_map:
                    item_map[key] = StudyProblemItemQuery(
                        study_problem_id=sp.study_problem_id.value,
                        problem_id=sp.problem_id.value,
                        problem_title=problem_info.problem_title if problem_info else "",
                        problem_tier_level=problem_info.problem_tier_level if problem_info else 0,
                        problem_tier_name=problem_info.problem_tier_name if problem_info else "",
                        problem_class_level=problem_info.problem_class_level if problem_info else None,
                        tags=list(problem_info.tags) if problem_info else [],
                        solve_info=[],
                    )
                    if date_str not in date_items:
                        date_order.append(date_str)
                        date_items[date_str] = []
                    date_items[date_str].append(key)

                user = user_map.get(member.user_account_id.value)
                if not user:
                    continue
                bj_id = user.bj_account_id
                solved = sp.problem_id.value in solved_map.get(bj_id, set())
                item_map[key].solve_info.append(
                    MemberSolveInfoQuery(
                        user_account_id=member.user_account_id.value,
                        bj_account_id=bj_id,
                        user_code=user.user_code,
                        solved=solved,
                        solve_date=None,
                    )
                )

        # 날짜 정렬 후 결과 조립
        date_order_sorted = sorted(date_order)
        study_data = [
            StudyDayDataQuery(
                target_date=date_str,
                problems=[item_map[k] for k in date_items[date_str]],
            )
            for date_str in date_order_sorted
        ]
        return StudyProblemsQuery(study_data=study_data)

    async def _fetch_problems_info(self, problem_ids: list[int]) -> ProblemsInfoQuery:
        if not problem_ids:
            return ProblemsInfoQuery(problems={})
        event = DomainEvent(
            event_type="GET_PROBLEM_INFOS_REQUESTED",
            data=GetProblemsInfoPayload(problem_ids=problem_ids),
            result_type=ProblemsInfoQuery
        )
        return await self.domain_event_bus.publish(event)
