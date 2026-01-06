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
                    WillSolveProblemModel.deleted_at.is_(None)
                )
            )
            .order_by(WillSolveProblemModel.marked_date.asc())
        )

        result = await self.session.execute(stmt)
        models = result.scalars().all()

        return [WillSolveProblemMapper.to_entity(model) for model in models]
    
    @override
    async def find_will_solve_problems_by_date(
        self,
        user_id: UserAccountId,
        target_date: date
    ) -> list[WillSolveProblem]:
        """날짜별 풀 예정 문제 조회"""
        stmt = (
            select(WillSolveProblemModel)
            .where(
                and_(
                    WillSolveProblemModel.user_account_id == user_id.value,
                    WillSolveProblemModel.marked_date == target_date,
                    WillSolveProblemModel.deleted_at.is_(None)
                )
            )
            # 날짜 내에서는 order 순으로 정렬하여 반환
            .order_by(WillSolveProblemModel.order.asc())
        )

        result = await self.session.execute(stmt)
        models = result.scalars().all()

        return [WillSolveProblemMapper.to_entity(model) for model in models]

    @override
    async def save_all_will_solve_problems(
        self, 
        will_solve_problems: list[WillSolveProblem]
    ) -> None:
        """일괄 저장 및 업데이트 (Upsert)"""
        if not will_solve_problems:
            return

        for entity in will_solve_problems:
            # 엔티티를 모델로 변환
            model = WillSolveProblemMapper.to_model(entity)
            
            # merge는 PK를 기준으로 기존 데이터가 있으면 UPDATE, 없으면 INSERT를 수행합니다.
            # 또한 세션에 모델을 등록하는 역할도 겸합니다.
            await self.session.merge(model)

        # 모든 merge가 끝나면 한 번에 flush하여 DB에 반영
        await self.session.flush()