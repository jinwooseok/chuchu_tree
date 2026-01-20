"""UserActivity Repository 구현"""
from calendar import monthrange
from datetime import date
from typing import override

from sqlalchemy import and_, extract, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload


from app.activity.domain.entity.problem_banned_record import ProblemBannedRecord
from app.activity.domain.entity.problem_record import ProblemRecord
from app.activity.domain.entity.user_activity import UserActivity
from app.activity.domain.entity.will_solve_problem import WillSolveProblem
from app.activity.domain.repository.user_activity_repository import UserActivityRepository
from app.activity.infra.mapper.problem_banned_record_mapper import ProblemBannedRecordMapper
from app.activity.infra.mapper.problem_record_mapper import ProblemRecordMapper
from app.activity.infra.mapper.will_solve_problem_mapper import WillSolveProblemMapper
from app.activity.infra.model.problem_banned_record import ProblemBannedRecordModel
from app.activity.infra.model.problem_record import ProblemRecordModel
from app.activity.infra.model.will_solve_problem import WillSolveProblemModel
from app.activity.infra.mapper.tag_customization_mapper import TagCustomizationMapper
from app.activity.infra.mapper.user_activity_mapper import UserActivityMapper
from app.activity.infra.model.tag_custom import TagCustomModel
from app.common.domain.vo.identifiers import UserAccountId
from app.core.database import Database
from app.user.infra.model.user_account import UserAccountModel


class UserActivityRepositoryImpl(UserActivityRepository):
    """UserActivity Repository 구현체"""

    def __init__(self, db: Database):
        self.db = db

    @property
    def session(self) -> AsyncSession:
        return self.db.get_current_session()

    @override
    async def find_by_user_account_id(
        self, user_account_id: UserAccountId
    ) -> UserActivity:
        # UserAccountModel을 기준으로 연관된 모든 활동 데이터를 한 번에 로드
        stmt = (
            select(UserAccountModel)
            .options(
                selectinload(UserAccountModel.tag_customs.and_(TagCustomModel.deleted_at.is_(None))),
                selectinload(UserAccountModel.banned_problems.and_(ProblemBannedRecordModel.deleted_at.is_(None))),
                selectinload(UserAccountModel.will_solve_problems.and_(WillSolveProblemModel.deleted_at.is_(None)))
            )
            .where(UserAccountModel.user_account_id == user_account_id.value)
        )

        result = await self.session.execute(stmt)
        user_account_model = result.scalar_one_or_none()

        # 매퍼에게 유저 계정 모델을 통째로 넘겨서 엔티티로 변환
        return UserActivityMapper.to_entity(
            user_account_id=user_account_model.user_account_id,
            tag_custom_models=user_account_model.tag_customs,
            will_solve_problem_models=user_account_model.will_solve_problems,
            problem_banned_record_models=user_account_model.banned_problems)

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
            .order_by(
                WillSolveProblemModel.marked_date.asc(), 
                WillSolveProblemModel.order.asc()
            )
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
    async def find_problem_records_by_date(
        self,
        user_id: UserAccountId,
        target_date: date
    ) -> list[ProblemRecord]:
        """날짜별 풀 예정 문제 조회"""
        stmt = (
            select(ProblemRecordModel)
            .where(
                and_(
                    ProblemRecordModel.user_account_id == user_id.value,
                    ProblemRecordModel.marked_date == target_date,
                    ProblemRecordModel.deleted_at.is_(None)
                )
            )
            # 날짜 내에서는 order 순으로 정렬하여 반환
            .order_by(ProblemRecordModel.order.asc())
        )

        result = await self.session.execute(stmt)
        models = result.scalars().all()

        return [ProblemRecordMapper.to_entity(model) for model in models]

    @override
    async def save_all_will_solve_problems(
        self, 
        will_solve_problems: list[WillSolveProblem]
    ) -> None:
        """일괄 저장 및 업데이트 (Upsert)"""
        if not will_solve_problems:
            return

        for entity in will_solve_problems:
            model = WillSolveProblemMapper.to_model(entity)
            await self.session.merge(model)
        await self.session.flush()
        
    @override
    async def save_all_problem_records(
        self, 
        problem_records: list[ProblemRecord]
    ) -> None:
        """일괄 저장 및 업데이트 (Upsert)"""
        if not problem_records:
            return

        for entity in problem_records:
            model = ProblemRecordMapper.to_model(entity)
            await self.session.merge(model)
        await self.session.flush()

    @override
    async def find_only_tag_custom_by_user_account_id(
        self, user_account_id: UserAccountId
    ) -> UserActivity:
        stmt = select(TagCustomModel).where(
            and_(
                TagCustomModel.user_account_id == user_account_id.value,
                TagCustomModel.deleted_at.is_(None),
            )
        )
        result = await self.session.execute(stmt)
        tag_custom_models = result.scalars().all()

        return UserActivityMapper.to_entity(
            user_account_id=user_account_id,
            tag_custom_models=tag_custom_models,
        )

    @override
    async def save_tag_custom(self, activity: UserActivity) -> None:
        if not activity.tag_customizations:
            return

        for entity in activity.tag_customizations:
            model = TagCustomizationMapper.to_model(entity)
            await self.session.merge(model)

        await self.session.flush()    
        
    @override
    async def find_only_banned_problem_by_user_account_id(self, user_account_id: UserAccountId) -> UserActivity:
        stmt = select(ProblemBannedRecordModel).where(
            and_(
                ProblemBannedRecordModel.user_account_id == user_account_id.value,
                ProblemBannedRecordModel.deleted_at.is_(None),
            )
        )
        result = await self.session.execute(stmt)
        problem_banned_record_models = result.scalars().all()

        return UserActivityMapper.to_entity(
            user_account_id=user_account_id,
            problem_banned_record_models=problem_banned_record_models,
        )

    
    @override
    async def save_problem_banned_record(self, activity: UserActivity):
        if not activity.banned_problems:
            return

        for entity in activity.banned_problems:
            model = ProblemBannedRecordMapper.to_model(entity)
            await self.session.merge(model)

        await self.session.flush()   