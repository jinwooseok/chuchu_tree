"""Streak Repository 구현"""

from datetime import date
from typing import override

from sqlalchemy import and_, func, select
from sqlalchemy.orm import aliased
from sqlalchemy.ext.asyncio import AsyncSession

from app.baekjoon.domain.entity.streak import Streak
from app.baekjoon.domain.repository.streak_repository import StreakRepository
from app.baekjoon.infra.mapper.streak_mapper import StreakMapper
from app.baekjoon.infra.model.problem_history import ProblemHistoryModel
from app.baekjoon.infra.model.streak import StreakModel
from app.common.domain.vo.identifiers import BaekjoonAccountId
from app.core.database import Database


class StreakRepositoryImpl(StreakRepository):
    """스트릭 Repository 구현체"""

    def __init__(self, db: Database):
        self.db = db

    @property
    def session(self) -> AsyncSession:
        return self.db.get_current_session()

    @override
    async def find_by_account_and_date_range(
        self,
        bj_account_id: BaekjoonAccountId,
        start_date: date,
        end_date: date
    ) -> list[Streak]:
        
        # 1. 날짜별로 그룹화하여 해당 날짜의 '마지막 누적 값' 추출
        # (하루에 데이터가 여러 개 쌓여도 가장 큰 값을 그날의 최종 누적으로 간주)
        daily_max_subq = (
            select(
                StreakModel.bj_account_id,
                StreakModel.streak_date,
                func.max(StreakModel.solved_count).label("max_cumulative_count")
            )
            .where(StreakModel.bj_account_id == bj_account_id.value)
            .group_by(StreakModel.streak_date)
        ).subquery()

        # 2. 그룹화된 데이터를 바탕으로 이전 날짜와의 차이 계산
        prev_solved_count = func.lag(daily_max_subq.c.max_cumulative_count).over(
            partition_by=daily_max_subq.c.bj_account_id,
            order_by=daily_max_subq.c.streak_date.asc()
        ).label("prev_count")

        calc_subq = (
            select(
                daily_max_subq.c.streak_date,
                daily_max_subq.c.bj_account_id,
                daily_max_subq.c.max_cumulative_count,
                prev_solved_count
            )
        ).subquery()

        # 3. 최종 필터링 및 뺄셈
        stmt = (
            select(
                calc_subq.c.streak_date,
                calc_subq.c.bj_account_id,
                # (오늘 최대 누적 - 어제 최대 누적)
                # 만약 첫 데이터라 NULL이면 0을 빼줌
                (calc_subq.c.max_cumulative_count - func.coalesce(calc_subq.c.prev_count, 0)).label("daily_solved_count")
            )
            .where(
                and_(
                    calc_subq.c.streak_date >= start_date,
                    calc_subq.c.streak_date <= end_date
                )
            )
            .order_by(calc_subq.c.streak_date.asc())
        )

        result = await self.session.execute(stmt)
        rows = result.all()

        return [StreakMapper.to_entity_from_row(row) for row in rows]
            