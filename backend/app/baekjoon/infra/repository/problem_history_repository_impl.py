"""ProblemHistory Repository 구현"""

from datetime import date
from typing import override

from sqlalchemy import and_, extract, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.baekjoon.domain.entity.problem_history import ProblemHistory
from app.baekjoon.domain.repository.problem_history_repository import ProblemHistoryRepository
from app.baekjoon.infra.mapper.problem_history_mapper import ProblemHistoryMapper
from app.baekjoon.infra.model.problem_history import ProblemHistoryModel
from app.baekjoon.infra.model.streak import StreakModel
from app.common.domain.vo.identifiers import BaekjoonAccountId
from app.core.database import Database


class ProblemHistoryRepositoryImpl(ProblemHistoryRepository):
    """문제 풀이 기록 Repository 구현체"""

    def __init__(self, db: Database):
        self.db = db

    @property
    def session(self) -> AsyncSession:
        return self.db.get_current_session()

    @override
    async def find_by_account_id(
        self,
        bj_account_id: BaekjoonAccountId
    ) -> list[ProblemHistory]:
        """백준 계정 ID로 모든 문제 풀이 기록 조회"""
        stmt = (
            select(ProblemHistoryModel)
            .where(ProblemHistoryModel.bj_account_id == bj_account_id.value)
            .order_by(ProblemHistoryModel.created_at.asc())
        )

        result = await self.session.execute(stmt)
        models = result.scalars().all()

        return [ProblemHistoryMapper.to_entity(model) for model in models]

    @override
    async def find_by_account_and_date_range(
        self,
        bj_account_id: BaekjoonAccountId,
        start_date: date,
        end_date: date
    ) -> list[ProblemHistory]:
        """백준 계정 ID와 날짜 범위로 문제 풀이 기록 조회"""
        stmt = (
            select(ProblemHistoryModel)
            .where(
                and_(
                    ProblemHistoryModel.bj_account_id == bj_account_id.value,
                    func.date(ProblemHistoryModel.created_at) >= start_date,
                    func.date(ProblemHistoryModel.created_at) <= end_date
                )
            )
            .order_by(ProblemHistoryModel.created_at.asc())
        )

        result = await self.session.execute(stmt)
        models = result.scalars().all()

        return [ProblemHistoryMapper.to_entity(model) for model in models]

    @override
    async def find_by_account_and_month_with_streak(
        self,
        bj_account_id: BaekjoonAccountId,
        year: int,
        month: int
    ) -> dict[int, date]:
        """백준 계정 ID와 년/월로 Streak과 연동된 문제 풀이 기록 조회"""
        stmt = (
            select(
                ProblemHistoryModel.problem_id,
                StreakModel.streak_date
            )
            .join(
                StreakModel,
                ProblemHistoryModel.streak_id == StreakModel.streak_id
            )
            .where(
                and_(
                    ProblemHistoryModel.bj_account_id == bj_account_id.value,
                    ProblemHistoryModel.streak_id.is_not(None),
                    extract('year', StreakModel.streak_date) == year,
                    extract('month', StreakModel.streak_date) == month
                )
            )
        )

        result = await self.session.execute(stmt)
        rows = result.all()

        # {problem_id: streak_date} 딕셔너리로 반환
        return {row.problem_id: row.streak_date for row in rows}
