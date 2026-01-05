"""UserActivity Repository 구현"""
from calendar import monthrange
from datetime import date
from typing import override

from sqlalchemy import and_, extract, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.activity.domain.entity.problem_record import ProblemRecord
from app.activity.domain.entity.user_activity import UserActivity
from app.activity.domain.entity.will_solve_problem import WillSolveProblem
from app.activity.domain.repository.user_activity_repository import UserActivityRepository
from app.activity.infra.mapper.problem_record_mapper import ProblemRecordMapper
from app.activity.infra.mapper.will_solve_problem_mapper import WillSolveProblemMapper
from app.activity.infra.model.problem_record import ProblemRecordModel
from app.activity.infra.model.will_solve_problem import WillSolveProblemModel
from app.common.domain.vo.identifiers import UserAccountId
from app.core.database import Database


class UserActivityRepositoryImpl(UserActivityRepository):
    """UserActivity Repository 구현체"""

    def __init__(self, db: Database):
        self.db = db

    @property
    def session(self) -> AsyncSession:
        return self.db.get_current_session()

    @override
    async def save(self, activity: UserActivity) -> UserActivity:
        """활동 저장 (구현 필요)"""
        raise NotImplementedError()

    @override
    async def find_by_user_id(self, user_id: UserAccountId) -> UserActivity | None:
        """유저 ID로 활동 조회 (구현 필요)"""
        raise NotImplementedError()

    @override
    async def find_will_solve_problems_by_date(
        self,
        user_id: UserAccountId,
        target_date: date
    ) -> list[WillSolveProblem]:
        """날짜별 풀 예정 문제 조회 (구현 필요)"""
        raise NotImplementedError()

    @override
    async def find_monthly_problem_records(
        self,
        user_id: UserAccountId,
        year: int,
        month: int
    ) -> list[ProblemRecord]:
        """월간 푼 문제 기록 조회"""
        # 해당 월의 첫날과 마지막날 계산
        _, last_day = monthrange(year, month)
        start_date = date(year, month, 1)
        end_date = date(year, month, last_day)

        stmt = (
            select(ProblemRecordModel)
            .where(
                and_(
                    ProblemRecordModel.user_account_id == user_id.value,
                    ProblemRecordModel.marked_date >= start_date,
                    ProblemRecordModel.marked_date <= end_date,
                    ProblemRecordModel.solved_yn == True,
                    ProblemRecordModel.deleted_at.is_(None)
                )
            )
            .order_by(ProblemRecordModel.marked_date.asc())
        )

        result = await self.session.execute(stmt)
        models = result.scalars().all()

        return [ProblemRecordMapper.to_entity(model) for model in models]

    @override
    async def find_monthly_will_solve_problems(
        self,
        user_id: UserAccountId,
        year: int,
        month: int
    ) -> list[WillSolveProblem]:
        """월간 풀 예정 문제 조회"""
        # 해당 월의 첫날과 마지막날 계산
        _, last_day = monthrange(year, month)
        start_date = date(year, month, 1)
        end_date = date(year, month, last_day)

        stmt = (
            select(WillSolveProblemModel)
            .where(
                and_(
                    WillSolveProblemModel.user_account_id == user_id.value,
                    WillSolveProblemModel.marked_date >= start_date,
                    WillSolveProblemModel.marked_date <= end_date,
                    WillSolveProblemModel.marked_yn == True,
                    WillSolveProblemModel.deleted_at.is_(None)
                )
            )
            .order_by(WillSolveProblemModel.marked_date.asc())
        )

        result = await self.session.execute(stmt)
        models = result.scalars().all()

        return [WillSolveProblemMapper.to_entity(model) for model in models]
