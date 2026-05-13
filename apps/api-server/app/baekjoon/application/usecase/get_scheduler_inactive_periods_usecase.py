"""스케줄러 미작동 구간 조회 Usecase"""

import logging
from datetime import date, timedelta

from app.baekjoon.application.query.scheduler_inactive_periods_query import (
    InactivePeriod,
    SchedulerInactivePeriodsQuery,
)
from app.baekjoon.domain.repository.baekjoon_account_repository import BaekjoonAccountRepository
from app.common.domain.repository.system_log_repository import SystemLogRepository
from app.common.domain.vo.identifiers import UserAccountId
from app.core.database import transactional
from app.core.error_codes import ErrorCode
from app.core.exception import APIException

logger = logging.getLogger(__name__)


class GetSchedulerInactivePeriodsUsecase:
    """스케줄러 미작동 구간 조회 Usecase"""

    def __init__(
        self,
        baekjoon_account_repository: BaekjoonAccountRepository,
        system_log_repository: SystemLogRepository,
    ):
        self.baekjoon_account_repository = baekjoon_account_repository
        self.system_log_repository = system_log_repository

    @transactional(readonly=True)
    async def execute(self, user_account_id: int) -> SchedulerInactivePeriodsQuery:
        """
        연동일부터 오늘까지 스케줄러 SUCCESS가 없는 날짜를 구간으로 반환

        Args:
            user_account_id: 유저 계정 ID

        Returns:
            SchedulerInactivePeriodsQuery: 미작동 구간 목록
        """
        ua_id = UserAccountId(user_account_id)

        # 1. BaekjoonAccount + 연동일 조회
        account_with_link = await self.baekjoon_account_repository.find_by_user_id_with_link_date(ua_id)
        if not account_with_link:
            raise APIException(ErrorCode.UNLINKED_USER)

        bj_account, linked_at = account_with_link

        # 2. 연동일 ~ 오늘 날짜 범위
        link_date: date = linked_at.date() if hasattr(linked_at, "date") else linked_at
        today = date.today()

        if link_date > today:
            return SchedulerInactivePeriodsQuery(
                bj_account_id=bj_account.bj_account_id.value,
                inactive_periods=[]
            )

        # 3. SUCCESS 날짜 조회
        success_dates: set[date] = await self.system_log_repository.find_scheduler_success_dates_by_bj_account(
            bj_account.bj_account_id
        )

        # 4. 연동일 ~ 오늘 사이 missing 날짜 계산
        missing_dates = []
        current = link_date
        while current <= today:
            if current not in success_dates:
                missing_dates.append(current)
            current += timedelta(days=1)

        # 5. 연속 구간으로 병합
        inactive_periods = self._merge_consecutive_dates(missing_dates)

        return SchedulerInactivePeriodsQuery(
            bj_account_id=bj_account.bj_account_id.value,
            inactive_periods=inactive_periods
        )

    def _merge_consecutive_dates(self, dates: list[date]) -> list[InactivePeriod]:
        """연속된 날짜를 구간으로 병합"""
        if not dates:
            return []

        sorted_dates = sorted(dates)
        periods: list[InactivePeriod] = []
        period_start = sorted_dates[0]
        period_end = sorted_dates[0]

        for d in sorted_dates[1:]:
            if d == period_end + timedelta(days=1):
                period_end = d
            else:
                periods.append(InactivePeriod(start_date=period_start, end_date=period_end))
                period_start = d
                period_end = d

        periods.append(InactivePeriod(start_date=period_start, end_date=period_end))
        return periods
