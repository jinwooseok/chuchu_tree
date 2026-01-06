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
        all_planned_ids = {pid for daily in activity_data.daily_activities for pid in daily.will_solve_problem_ids}
        actually_solved_ids_ever = await self.problem_history_repository.find_solved_ids_in_list(
            bj_account.bj_account_id, list(all_planned_ids)
        )

        # 5. 문제 상세 정보 조회 (Problem Domain)
        # 계획된 문제 + 이번 달 실제로 푼 문제들의 상세 정보 통합 요청
        all_problem_ids = all_planned_ids | set(real_solved_by_date.keys())
        problems_info = await self._fetch_problems_info(all_problem_ids)

        # 6. 일별 데이터 조립
        monthly_data = []
        for daily in activity_data.daily_activities:
            target_date = daily.target_date

            # [핵심 로직] 풀 예정 목록에서 '전체 이력 중 풀린 적 있는 문제' 제거
            # 11월에 풀었든, 오늘 풀었든, 앞으로 풀든 히스토리에 있으면 will_solve에서 빠짐
            actual_will_solve_ids = [
                pid for pid in daily.will_solve_problem_ids 
                if pid not in actually_solved_ids_ever
            ]

            # [핵심 로직] 푼 문제 목록 조립
            # 활동 기록상 solved + '실제 이 날짜에 스트릭이 찍힌 문제'
            real_solved_on_this_date = {
                pid for pid, s_date in real_solved_by_date.items() if s_date == target_date
            }
            all_solved_ids = set(daily.solved_problem_ids) | real_solved_on_this_date

            # 결과 매핑
            solved_problems = [
                SolvedProblemQuery(**problems_info.problems[pid].model_dump(), real_solved_yn=True)
                for pid in all_solved_ids if pid in problems_info.problems
            ]

            will_solve_problems = [
                problems_info.problems[pid]
                for pid in actual_will_solve_ids if pid in problems_info.problems
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
            event_type="GET_PROBLEMS_INFO_REQUESTED",
            data=GetProblemsInfoPayload(problem_ids=list(problem_ids)),
            result_type=ProblemsInfoQuery
        )
        return await self.domain_event_bus.publish(event)