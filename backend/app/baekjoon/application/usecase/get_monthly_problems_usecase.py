# 필요한 임포트 추가
from collections import defaultdict
from datetime import date
from dataclasses import dataclass
from calendar import monthrange

# 기존 임포트 유지
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

# ProblemEntry 데이터 클래스 정의
@dataclass
class ProblemEntry:
    problem_id: int
    display_date: date  # The date this problem should be displayed on
    order: int          # Order within the day
    is_solved: bool     # True if solved (streak or problem record), False if will_solve
    is_streak: bool     # True if it originated from a streak
    source: str         # 'streak', 'record', 'will_solve' (for debugging/clarity)

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

        # 4. 계획된 문제(Will Solve) 중 전체 이력에서 해결 여부 확인 (기존 로직 유지)
        all_planned_ids = {pid for daily in activity_data.daily_activities for pid in daily.will_solve_problem_ids}
        # 실제로 풀었는지 여부는 이제 merging logic에서 최종적으로 결정되므로, 여기서 필터링은 제거함.
        # 기존 코드에서 `actually_solved_ids_ever`는 사용처가 사라지므로 필요없으나,
        # _fetch_problems_info에서 모든 problem id를 모을때 사용될 수 있으므로 일단 남겨둡니다.
        # 다만 현재 로직상 all_problem_ids_for_detail에 이미 포함될 것이므로 제거해도 무방합니다.
        # 여기서는 단순히 _fetch_problems_info에서 사용할 모든 ID를 모으는 용도로만 사용.
        
        # 5. 문제 상세 정보 조회 (Problem Domain)
        # 모든 가능한 문제 ID를 수집하여 상세 정보를 한 번에 조회합니다.
        all_problem_ids_for_detail = set()
        for daily in activity_data.daily_activities:
            all_problem_ids_for_detail.update(daily.solved_problem_ids)
            all_problem_ids_for_detail.update(daily.will_solve_problem_ids)
        all_problem_ids_for_detail.update(real_solved_by_date.keys())
        # 이전 all_planned_ids | set(real_solved_by_date.keys()) 대신 위 로직으로 변경.
        
        problems_info = await self._fetch_problems_info(all_problem_ids_for_detail)
        
        # 6. 데이터 병합 및 우선순위 적용
        merged_problem_map: dict[int, ProblemEntry] = {}

        # a. Streaks 우선 처리
        for problem_id, solved_date in real_solved_by_date.items():
            merged_problem_map[problem_id] = ProblemEntry(
                problem_id=problem_id,
                display_date=solved_date,
                order=-1,  # Placeholder, will be updated by record if available on same day
                is_solved=True,
                is_streak=True,
                source='streak'
            )

        # b. Problem Records 처리 (streak보다 후순위, will_solve보다 선순위)
        for daily in activity_data.daily_activities:
            current_date = daily.target_date
            for index, problem_id in enumerate(daily.solved_problem_ids):
                if problem_id in merged_problem_map:
                    existing_entry = merged_problem_map[problem_id]
                    # Rule 6 (Order priority): 동일 날짜에 streak과 record가 있으면 record의 order를 따름
                    if existing_entry.display_date == current_date:
                        existing_entry.order = index
                    # Rule 7 (Date priority): 날짜가 다른 경우 streak 날짜를 따름 (이미 streak이 설정했으므로 변경 없음)
                    # solved_yn은 이미 True로 유지. is_streak도 기존값을 유지.
                else:
                    # Streak이 없는 Problem Record
                    merged_problem_map[problem_id] = ProblemEntry(
                        problem_id=problem_id,
                        display_date=current_date,
                        order=index,
                        is_solved=True, # ProblemRecord.solved=True인 경우만 여기에 들어옴
                        is_streak=False,
                        source='record'
                    )

        # c. Will Solve Problems 처리 (가장 낮은 우선순위)
        for daily in activity_data.daily_activities:
            current_date = daily.target_date
            for index, problem_id in enumerate(daily.will_solve_problem_ids):
                # Rule 8 (Record/Streak priority over will_solve):
                # merged_problem_map에 없어야만 will_solve로 추가
                if problem_id not in merged_problem_map:
                    merged_problem_map[problem_id] = ProblemEntry(
                        problem_id=problem_id,
                        display_date=current_date,
                        order=index,
                        is_solved=False, # Will solve 문제이므로 solved는 False
                        is_streak=False,
                        source='will_solve'
                    )
        
        # 7. 일별 데이터 재조립 및 최종 형식으로 변환
        final_daily_data = defaultdict(lambda: {'solved_problems': [], 'will_solve_problems': []})
        all_processed_problem_ids = set()

        for entry in merged_problem_map.values():
            problem_info = problems_info.problems.get(entry.problem_id)
            if not problem_info:
                logger.warning(f"Problem ID {entry.problem_id} not found in problems_info. Skipping.")
                continue

            all_processed_problem_ids.add(entry.problem_id)

            if entry.is_solved:
                final_daily_data[entry.display_date]['solved_problems'].append(
                    (entry.order, SolvedProblemQuery(**problem_info.model_dump(), real_solved_yn=entry.is_streak))
                )
            else: # is_solved is False, meaning it's a will_solve problem
                final_daily_data[entry.display_date]['will_solve_problems'].append(
                    (entry.order, problem_info) # ProblemInfoQuery is sufficient for will_solve
                )

        monthly_data_list = []
        _, last_day = monthrange(command.year, command.month)

        for day in range(1, last_day + 1):
            current_date = date(command.year, command.month, day)
            day_data = final_daily_data[current_date]

            sorted_solved = sorted(day_data['solved_problems'], key=lambda x: x[0])
            sorted_will_solve = sorted(day_data['will_solve_problems'], key=lambda x: x[0])

            # Extract the query objects from the sorted tuples
            solved_queries = [item[1] for item in sorted_solved]
            will_solve_queries = [item[1] for item in sorted_will_solve]

            monthly_data_list.append(MonthlyDayDataQuery(
                target_date=current_date.isoformat(),
                solved_problem_count=len(solved_queries),
                will_solve_problem_count=len(will_solve_queries),
                solved_problems=solved_queries,
                will_solve_problems=will_solve_queries
            ))

        return MonthlyProblemsQuery(
            total_problem_count=len(all_processed_problem_ids),
            monthly_data=monthly_data_list
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