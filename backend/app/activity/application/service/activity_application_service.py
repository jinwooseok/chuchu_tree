"""Activity Application Service"""
import logging
from calendar import monthrange
from collections import defaultdict
from datetime import date

from app.activity.application.query.monthly_activity_data_query import (
    DailyActivityQuery,
    MonthlyActivityDataQuery
)
from app.activity.domain.repository.user_activity_repository import UserActivityRepository
from app.baekjoon.domain.event.get_monthly_activity_data_payload import GetMonthlyActivityDataPayload
from app.common.domain.vo.identifiers import UserAccountId
from app.common.infra.event.decorators import event_handler
from app.core.database import transactional

logger = logging.getLogger(__name__)


class ActivityApplicationService:
    """Activity Application Service"""

    def __init__(
        self,
        user_activity_repository: UserActivityRepository
    ):
        self.user_activity_repository = user_activity_repository

    @event_handler("GET_MONTHLY_ACTIVITY_DATA_REQUESTED")
    @transactional
    async def get_monthly_activity_data(
        self,
        payload: GetMonthlyActivityDataPayload
    ) -> MonthlyActivityDataQuery:
        """
        월간 활동 데이터 조회
        Args:
            payload: 월간 활동 데이터 조회 요청
        Returns:
            MonthlyActivityDataQuery: 월간 활동 데이터
        """
        user_account_id = UserAccountId(payload.user_account_id)

        # 1. 월간 푼 문제 기록 조회
        problem_records = await self.user_activity_repository.find_monthly_problem_records(
            user_id=user_account_id,
            year=payload.year,
            month=payload.month
        )

        # 2. 월간 풀 예정 문제 조회
        will_solve_problems = await self.user_activity_repository.find_monthly_will_solve_problems(
            user_id=user_account_id,
            year=payload.year,
            month=payload.month
        )

        # 3. 날짜별로 그룹화
        daily_map = defaultdict(lambda: {"solved": set(), "will_solve": set()})

        for record in problem_records:
            if record.solved:
                daily_map[record.marked_date]["solved"].add(record.problem_id.value)

        for will_solve in will_solve_problems:
            daily_map[will_solve.marked_date]["will_solve"].add(will_solve.problem_id.value)

        # 4. 해당 월의 모든 날짜 생성 (데이터가 없는 날도 포함)
        _, last_day = monthrange(payload.year, payload.month)
        daily_activities = []

        for day in range(1, last_day + 1):
            target_date = date(payload.year, payload.month, day)
            day_data = daily_map.get(target_date, {"solved": set(), "will_solve": set()})

            daily_activities.append(DailyActivityQuery(
                target_date=target_date,
                solved_problem_ids=list(day_data["solved"]),
                will_solve_problem_ids=list(day_data["will_solve"])
            ))

        # 5. 전체 문제 수 계산
        total_problem_ids = set()
        for day_data in daily_map.values():
            total_problem_ids.update(day_data["solved"])
            total_problem_ids.update(day_data["will_solve"])

        return MonthlyActivityDataQuery(
            daily_activities=daily_activities,
            total_problem_count=len(total_problem_ids)
        )
