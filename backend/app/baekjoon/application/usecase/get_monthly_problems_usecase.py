"""월간 문제 조회 Usecase"""
import logging
from datetime import datetime

from app.activity.application.query.monthly_activity_data_query import MonthlyActivityDataQuery
from app.baekjoon.application.command.get_monthly_problems_command import GetMonthlyProblemsCommand
from app.baekjoon.application.query.monthly_problems_query import (
    MonthlyDayDataQuery,
    MonthlyProblemsQuery,
    SolvedProblemQuery
)
from app.baekjoon.domain.event.get_monthly_activity_data_payload import GetMonthlyActivityDataPayload
from app.baekjoon.domain.event.get_problems_info_payload import GetProblemsInfoPayload
from app.baekjoon.domain.repository.baekjoon_account_repository import BaekjoonAccountRepository
from app.baekjoon.domain.repository.problem_history_repository import ProblemHistoryRepository
from app.common.domain.entity.domain_event import DomainEvent
from app.common.domain.service.event_publisher import DomainEventBus
from app.common.domain.vo.identifiers import UserAccountId
from app.core.database import transactional
from app.core.error_codes import ErrorCode
from app.core.exception import APIException
from app.problem.application.query.problems_info_query import ProblemsInfoQuery, ProblemInfoQuery

logger = logging.getLogger(__name__)


class GetMonthlyProblemsUsecase:
    """월간 문제 조회 Usecase"""

    def __init__(
        self,
        baekjoon_account_repository: BaekjoonAccountRepository,
        problem_history_repository: ProblemHistoryRepository,
        domain_event_bus: DomainEventBus
    ):
        self.baekjoon_account_repository = baekjoon_account_repository
        self.problem_history_repository = problem_history_repository
        self.domain_event_bus = domain_event_bus

    @transactional
    async def execute(self, command: GetMonthlyProblemsCommand) -> MonthlyProblemsQuery:
        user_account_id = UserAccountId(command.user_account_id)

        # 1. Activity domain 데이터 요청 (월간 활동 계획 및 기록)
        activity_data = await self._fetch_activity_data(command)
        
        # 2. 백준 계정 조회
        bj_account = await self.baekjoon_account_repository.find_by_user_id(user_account_id)
        if not bj_account:
            raise APIException(ErrorCode.INVALID_REQUEST)

        # 3. 이번 달 실제 풀이 이력 조회 (날짜별 스트릭 기준)
        # {problem_id: solved_date}
        real_solved_by_date = await self.problem_history_repository.find_by_account_and_month_with_streak(
            bj_account.bj_account_id, command.year, command.month
        )

        # 4. 계획된 문제(Will Solve) 중 전체 이력에서 해결 여부 확인
        # (이번 달 계획된 모든 ID를 모아서 한 번에 조회)
        print(activity_data.daily_activities)
        all_planned_ids = {pid for daily in activity_data.daily_activities for pid in daily.will_solve_problem_ids}
        actually_solved_ids_ever = await self.problem_history_repository.find_solved_ids_in_list(
            bj_account.bj_account_id, list(all_planned_ids)
        )
        print(actually_solved_ids_ever)
        # 5. 문제 상세 정보 조회 (Problem Domain)
        # 계획된 문제 + 이번 달 실제로 푼 문제들의 상세 정보 통합 요청
        all_problem_ids = all_planned_ids | set(real_solved_by_date.keys())
        problems_info = await self._fetch_problems_info(all_problem_ids)
        
        # 6. 일별 데이터 조립
        monthly_data = []
        for daily in activity_data.daily_activities:
            target_date = daily.target_date

            # [수정] 1. 'will_solve' 목록 필터링 (순서 보존)
            # daily.will_solve_problem_ids는 이미 order 순으로 정렬된 list입니다.
            actual_will_solve_ids = [
                pid for pid in daily.will_solve_problem_ids 
                if pid not in actually_solved_ids_ever  # 전체 이력에 있으면 제외
            ]

            # [수정] 2. 'solved' 목록 조립
            # 여기서는 순서가 덜 중요할 수 있지만, 필요하다면 정렬 로직을 넣을 수 있습니다.
            real_solved_on_this_date = {
                pid for pid, s_date in real_solved_by_date.items() if s_date == target_date
            }
            # set 연산으로 중복을 제거한 뒤 최종 리스트로 만듭니다.
            all_solved_ids = set(daily.solved_problem_ids) | real_solved_on_this_date

            # [수정] 3. 상세 정보 매핑 (리스트 순서대로)
            # actual_will_solve_ids 리스트가 이미 order 순이므로 결과도 order 순이 됩니다.
            will_solve_problems = [
                problems_info.problems[pid]
                for pid in actual_will_solve_ids 
                if pid in problems_info.problems
            ]

            solved_problems = [
                SolvedProblemQuery(**problems_info.problems[pid].model_dump(), real_solved_yn=True)
                for pid in all_solved_ids if pid in problems_info.problems
            ]

            monthly_data.append(MonthlyDayDataQuery(
                target_date=target_date.isoformat(),
                solved_problem_count=len(solved_problems),
                will_solve_problem_count=len(will_solve_problems),
                solved_problems=solved_problems,
                will_solve_problems=will_solve_problems
            ))

        return MonthlyProblemsQuery(
            total_problem_count=activity_data.total_problem_count,
            monthly_data=monthly_data
        )

    async def _fetch_activity_data(self, command: GetMonthlyProblemsCommand) -> MonthlyActivityDataQuery:
        event = DomainEvent(
            event_type="GET_MONTHLY_ACTIVITY_DATA_REQUESTED",
            data=GetMonthlyActivityDataPayload(
                user_account_id=command.user_account_id,
                year=command.year,
                month=command.month
            ),
            result_type=MonthlyActivityDataQuery
        )
        data = await self.domain_event_bus.publish(event)
        if not data:
            raise APIException(ErrorCode.INVALID_REQUEST)
        return data

    async def _fetch_problems_info(self, problem_ids: set[int]) -> ProblemsInfoQuery:
        if not problem_ids:
            return ProblemsInfoQuery(problems={})
        event = DomainEvent(
            event_type="GET_PROBLEM_INFOS_REQUESTED",
            data=GetProblemsInfoPayload(problem_ids=list(problem_ids)),
            result_type=ProblemsInfoQuery
        )
        return await self.domain_event_bus.publish(event)