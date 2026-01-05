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
        domain_event_bus: DomainEventBus
    ):
        self.baekjoon_account_repository = baekjoon_account_repository
        self.domain_event_bus = domain_event_bus

    @transactional
    async def execute(self, command: GetMonthlyProblemsCommand) -> MonthlyProblemsQuery:
        """
        월간 문제 조회
        Args:
            command: 월간 문제 조회 명령
        Returns:
            MonthlyProblemsQuery: 월간 문제 데이터
        """
        user_account_id = UserAccountId(command.user_account_id)

        # 1. Activity domain에 월간 활동 데이터 요청 (이벤트 발행)
        activity_event = DomainEvent(
            event_type="GET_MONTHLY_ACTIVITY_DATA_REQUESTED",
            data=GetMonthlyActivityDataPayload(
                user_account_id=command.user_account_id,
                year=command.year,
                month=command.month
            ),
            result_type=MonthlyActivityDataQuery
        )
        activity_data: MonthlyActivityDataQuery = await self.domain_event_bus.publish(activity_event)

        if not activity_data:
            logger.error(f"[GetMonthlyProblemsUsecase] 활동 데이터를 찾을 수 없음: user_account_id={command.user_account_id}, month={command.month}")
            raise APIException(ErrorCode.INVALID_REQUEST)

        # 2. BaekjoonAccount 조회 (ProblemHistory 포함)
        bj_account = await self.baekjoon_account_repository.find_by_user_id(user_account_id)
        if not bj_account:
            logger.error(f"[GetMonthlyProblemsUsecase] 백준 계정을 찾을 수 없음: user_account_id={command.user_account_id}")
            raise APIException(ErrorCode.INVALID_REQUEST)

        # 3. realSolvedYn 판별을 위한 문제 ID 집합 생성
        real_solved_problem_ids = {history.problem_id.value for history in bj_account.problem_histories}

        # 4. 모든 문제 ID 수집
        all_problem_ids = set()
        for daily in activity_data.daily_activities:
            all_problem_ids.update(daily.solved_problem_ids)
            all_problem_ids.update(daily.will_solve_problem_ids)

        # 5. Problem domain에 문제 정보 요청 (이벤트 발행)
        if all_problem_ids:
            problem_event = DomainEvent(
                event_type="GET_PROBLEMS_INFO_REQUESTED",
                data=GetProblemsInfoPayload(problem_ids=list(all_problem_ids)),
                result_type=ProblemsInfoQuery
            )
            problems_info: ProblemsInfoQuery = await self.domain_event_bus.publish(problem_event)
        else:
            problems_info = ProblemsInfoQuery(problems={})

        # 6. 일별 데이터 조립
        monthly_data = []
        for daily in activity_data.daily_activities:
            # 푼 문제 목록 (realSolvedYn 포함)
            solved_problems = []
            for problem_id in daily.solved_problem_ids:
                problem_info = problems_info.problems.get(problem_id)
                if problem_info:
                    solved_problems.append(SolvedProblemQuery(
                        **problem_info.model_dump(),
                        real_solved_yn=problem_id in real_solved_problem_ids
                    ))

            # 풀 예정 문제 목록
            will_solve_problems = []
            for problem_id in daily.will_solve_problem_ids:
                problem_info = problems_info.problems.get(problem_id)
                if problem_info:
                    will_solve_problems.append(problem_info)

            monthly_data.append(MonthlyDayDataQuery(
                target_date=daily.target_date.isoformat(),
                solved_problem_count=len(solved_problems),
                will_solve_problem_count=len(will_solve_problems),
                solved_problems=solved_problems,
                will_solve_problems=will_solve_problems
            ))

        return MonthlyProblemsQuery(
            total_problem_count=activity_data.total_problem_count,
            monthly_data=monthly_data
        )
