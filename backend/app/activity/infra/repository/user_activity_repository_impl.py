"""UserActivity Repository 구현 - 정규화된 테이블 구조"""
from calendar import monthrange
from datetime import date
from typing import override

from sqlalchemy import and_, delete, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.activity.domain.entity.user_activity import UserActivity
from app.activity.domain.entity.user_problem_status import UserProblemStatus
from app.activity.domain.repository.user_activity_repository import UserActivityRepository
from app.activity.infra.mapper.tag_customization_mapper import TagCustomizationMapper
from app.activity.infra.mapper.user_activity_mapper import UserActivityMapper
from app.activity.infra.mapper.user_problem_status_mapper import UserProblemStatusMapper
from app.activity.infra.model.user_problem_status import UserProblemStatusModel
from app.activity.infra.model.problem_date_record import ProblemDateRecordModel, RecordType
from app.activity.infra.model.tag_custom import TagCustomModel
from app.common.domain.vo.identifiers import UserAccountId
from app.core.database import Database
from app.user.infra.model.account_link import AccountLinkModel
from app.user.infra.model.user_account import UserAccountModel


class UserActivityRepositoryImpl(UserActivityRepository):
    """UserActivity Repository 구현체

    정규화된 테이블 구조:
    - UserProblemStatusModel: 문제별 마스터 (1:N의 1)
    - ProblemDateRecordModel: 날짜별 디테일 (1:N의 N)
    """

    def __init__(self, db: Database):
        self.db = db

    @property
    def session(self) -> AsyncSession:
        return self.db.get_current_session()

    async def _get_active_bj_account_id(self, user_account_id_value: int) -> str | None:
        """현재 활성 BJ 계정 ID 조회 (account_link.deleted_at IS NULL)"""
        stmt = (
            select(AccountLinkModel.bj_account_id)
            .where(
                and_(
                    AccountLinkModel.user_account_id == user_account_id_value,
                    AccountLinkModel.deleted_at.is_(None)
                )
            )
            .limit(1)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    @override
    async def find_by_user_account_id(
        self, user_account_id: UserAccountId
    ) -> UserActivity:
        """유저의 모든 활동 데이터를 한 번에 로드 (활성 BJ 계정 기준)"""
        active_bj_id = await self._get_active_bj_account_id(user_account_id.value)

        # Tag customs
        tag_stmt = select(TagCustomModel).where(
            and_(
                TagCustomModel.user_account_id == user_account_id.value,
                TagCustomModel.deleted_at.is_(None)
            )
        )
        tag_result = await self.session.execute(tag_stmt)
        tag_customs = tag_result.scalars().all()

        # Problem statuses: 활성 BJ 계정의 SOLVED/WILL_SOLVE + 모든 BANNED (bj_account_id=NULL)
        status_stmt = (
            select(UserProblemStatusModel)
            .options(
                selectinload(
                    UserProblemStatusModel.date_records.and_(ProblemDateRecordModel.deleted_at.is_(None))
                )
            )
            .where(
                and_(
                    UserProblemStatusModel.user_account_id == user_account_id.value,
                    UserProblemStatusModel.deleted_at.is_(None),
                    or_(
                        UserProblemStatusModel.bj_account_id == active_bj_id,
                        and_(
                            UserProblemStatusModel.bj_account_id.is_(None),
                            UserProblemStatusModel.banned_yn == True
                        )
                    )
                )
            )
        )
        status_result = await self.session.execute(status_stmt)
        problem_statuses = status_result.scalars().unique().all()

        return UserActivityMapper.to_entity(
            user_account_id=user_account_id,
            tag_custom_models=tag_customs,
            problem_status_models=problem_statuses
        )

    @override
    async def find_monthly_problem_records(
        self,
        user_id: UserAccountId,
        year: int,
        month: int
    ) -> list[UserProblemStatus]:
        """월간 푼 문제 기록 조회 (solved_yn=true, record_type='SOLVED', 활성 BJ 계정)"""
        _, last_day = monthrange(year, month)
        start_date = date(year, month, 1)
        end_date = date(year, month, last_day)

        active_bj_id = await self._get_active_bj_account_id(user_id.value)

        stmt = (
            select(UserProblemStatusModel)
            .join(ProblemDateRecordModel)
            .options(selectinload(UserProblemStatusModel.date_records))
            .where(
                and_(
                    UserProblemStatusModel.user_account_id == user_id.value,
                    UserProblemStatusModel.bj_account_id == active_bj_id,
                    UserProblemStatusModel.solved_yn == True,
                    UserProblemStatusModel.deleted_at.is_(None),
                    ProblemDateRecordModel.marked_date >= start_date,
                    ProblemDateRecordModel.marked_date <= end_date,
                    ProblemDateRecordModel.record_type == RecordType.SOLVED,
                    ProblemDateRecordModel.deleted_at.is_(None)
                )
            )
            .order_by(
                ProblemDateRecordModel.marked_date.asc(),
                ProblemDateRecordModel.display_order.asc()
            )
        )

        result = await self.session.execute(stmt)
        status_models = result.scalars().unique().all()

        statuses = []
        for status_model in status_models:
            for dr_model in status_model.date_records:
                if (dr_model.record_type == RecordType.SOLVED and
                        dr_model.deleted_at is None and
                        start_date <= dr_model.marked_date <= end_date):
                    statuses.append(UserProblemStatusMapper.status_to_entity(
                        status_model, [dr_model]
                    ))

        return sorted(statuses, key=lambda s: s.marked_date)

    @override
    async def find_monthly_will_solve_problems(
        self,
        user_id: UserAccountId,
        year: int,
        month: int
    ) -> list[UserProblemStatus]:
        """월간 풀 예정 문제 조회 (solved_yn=false, banned_yn=false, 활성 BJ 계정)"""
        _, last_day = monthrange(year, month)
        start_date = date(year, month, 1)
        end_date = date(year, month, last_day)

        active_bj_id = await self._get_active_bj_account_id(user_id.value)

        stmt = (
            select(UserProblemStatusModel)
            .join(ProblemDateRecordModel)
            .options(selectinload(UserProblemStatusModel.date_records))
            .where(
                and_(
                    UserProblemStatusModel.user_account_id == user_id.value,
                    UserProblemStatusModel.bj_account_id == active_bj_id,
                    UserProblemStatusModel.solved_yn == False,
                    UserProblemStatusModel.deleted_at.is_(None),
                    ProblemDateRecordModel.marked_date >= start_date,
                    ProblemDateRecordModel.marked_date <= end_date,
                    ProblemDateRecordModel.record_type == RecordType.WILL_SOLVE,
                    ProblemDateRecordModel.deleted_at.is_(None)
                )
            )
            .order_by(
                ProblemDateRecordModel.marked_date.asc(),
                ProblemDateRecordModel.display_order.asc()
            )
        )

        result = await self.session.execute(stmt)
        status_models = result.scalars().unique().all()

        statuses = []
        for status_model in status_models:
            for dr_model in status_model.date_records:
                if (dr_model.record_type == RecordType.WILL_SOLVE and
                        dr_model.deleted_at is None and
                        start_date <= dr_model.marked_date <= end_date):
                    statuses.append(UserProblemStatusMapper.status_to_entity(
                        status_model, [dr_model]
                    ))

        return sorted(statuses, key=lambda s: (s.marked_date, s.order))

    @override
    async def find_will_solve_problems_by_date(
        self,
        user_id: UserAccountId,
        target_date: date
    ) -> list[UserProblemStatus]:
        """날짜별 풀 예정 문제 조회 (활성 BJ 계정)"""
        active_bj_id = await self._get_active_bj_account_id(user_id.value)

        stmt = (
            select(UserProblemStatusModel)
            .join(ProblemDateRecordModel)
            .options(selectinload(UserProblemStatusModel.date_records))
            .where(
                and_(
                    UserProblemStatusModel.user_account_id == user_id.value,
                    UserProblemStatusModel.bj_account_id == active_bj_id,
                    UserProblemStatusModel.solved_yn == False,
                    UserProblemStatusModel.deleted_at.is_(None),
                    ProblemDateRecordModel.marked_date == target_date,
                    ProblemDateRecordModel.record_type == RecordType.WILL_SOLVE,
                    ProblemDateRecordModel.deleted_at.is_(None)
                )
            )
            .order_by(ProblemDateRecordModel.display_order.asc())
        )

        result = await self.session.execute(stmt)
        status_models = result.scalars().unique().all()

        statuses = []
        for status_model in status_models:
            for dr_model in status_model.date_records:
                if (dr_model.record_type == RecordType.WILL_SOLVE and
                        dr_model.deleted_at is None and
                        dr_model.marked_date == target_date):
                    statuses.append(UserProblemStatusMapper.status_to_entity(
                        status_model, [dr_model]
                    ))

        return sorted(statuses, key=lambda s: s.order)

    @override
    async def find_problem_records_by_date(
        self,
        user_id: UserAccountId,
        target_date: date
    ) -> list[UserProblemStatus]:
        """날짜별 푼 문제 조회 (활성 BJ 계정)"""
        active_bj_id = await self._get_active_bj_account_id(user_id.value)

        stmt = (
            select(UserProblemStatusModel)
            .join(ProblemDateRecordModel)
            .options(selectinload(UserProblemStatusModel.date_records))
            .where(
                and_(
                    UserProblemStatusModel.user_account_id == user_id.value,
                    UserProblemStatusModel.bj_account_id == active_bj_id,
                    UserProblemStatusModel.solved_yn == True,
                    UserProblemStatusModel.deleted_at.is_(None),
                    ProblemDateRecordModel.marked_date == target_date,
                    ProblemDateRecordModel.record_type == RecordType.SOLVED,
                    ProblemDateRecordModel.deleted_at.is_(None)
                )
            )
            .order_by(ProblemDateRecordModel.display_order.asc())
        )

        result = await self.session.execute(stmt)
        status_models = result.scalars().unique().all()

        statuses = []
        for status_model in status_models:
            for dr_model in status_model.date_records:
                if (dr_model.record_type == RecordType.SOLVED and
                        dr_model.deleted_at is None and
                        dr_model.marked_date == target_date):
                    statuses.append(UserProblemStatusMapper.status_to_entity(
                        status_model, [dr_model]
                    ))

        return sorted(statuses, key=lambda s: s.order)

    async def _get_existing_status(
        self,
        user_account_id: int,
        problem_id: int,
        bj_account_id: str | None
    ) -> UserProblemStatusModel | None:
        """기존 status 조회 (bj_account_id 스코핑 포함)"""
        if bj_account_id is None:
            # BANNED 레코드: bj_account_id IS NULL
            stmt = select(UserProblemStatusModel).where(
                and_(
                    UserProblemStatusModel.user_account_id == user_account_id,
                    UserProblemStatusModel.problem_id == problem_id,
                    UserProblemStatusModel.bj_account_id.is_(None)
                )
            )
        else:
            stmt = select(UserProblemStatusModel).where(
                and_(
                    UserProblemStatusModel.user_account_id == user_account_id,
                    UserProblemStatusModel.problem_id == problem_id,
                    UserProblemStatusModel.bj_account_id == bj_account_id
                )
            )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def _save_status_with_date_records(self, entity: UserProblemStatus) -> None:
        """UserProblemStatus (+ date_records) 저장 - Upsert"""
        existing_status = await self._get_existing_status(
            entity.user_account_id.value,
            entity.problem_id.value,
            entity.bj_account_id
        )

        status_model = UserProblemStatusMapper.entity_to_status_model(entity, existing_status)
        if not existing_status:
            self.session.add(status_model)
            await self.session.flush()

        for date_record in entity.date_records:
            if date_record.problem_date_record_id:
                dr_stmt = select(ProblemDateRecordModel).where(
                    ProblemDateRecordModel.problem_date_record_id == date_record.problem_date_record_id
                )
                dr_result = await self.session.execute(dr_stmt)
                existing_dr = dr_result.scalar_one_or_none()

                dr_model = UserProblemStatusMapper.entity_to_date_record_model(
                    date_record, status_model.user_problem_status_id, existing_dr
                )
                if not existing_dr:
                    self.session.add(dr_model)
            else:
                # 새 SOLVED 생성 시 활성 SOLVED 중복 방지 (Req 3)
                if date_record.record_type == RecordType.SOLVED:
                    dup_stmt = select(ProblemDateRecordModel).where(
                        and_(
                            ProblemDateRecordModel.user_problem_status_id == status_model.user_problem_status_id,
                            ProblemDateRecordModel.record_type == RecordType.SOLVED,
                            ProblemDateRecordModel.deleted_at.is_(None)
                        )
                    )
                    dup_result = await self.session.execute(dup_stmt)
                    if dup_result.scalar_one_or_none():
                        continue  # 이미 활성 SOLVED 존재 → skip

                dr_model = UserProblemStatusMapper.entity_to_date_record_model(
                    date_record, status_model.user_problem_status_id
                )
                self.session.add(dr_model)

    @override
    async def save_all_will_solve_problems(
        self,
        statuses: list[UserProblemStatus]
    ) -> None:
        """풀 예정 문제 일괄 저장 (Upsert)"""
        if not statuses:
            return
        for entity in statuses:
            await self._save_status_with_date_records(entity)
        await self.session.flush()

    @override
    async def save_all_problem_records(
        self,
        statuses: list[UserProblemStatus]
    ) -> None:
        """푼 문제 일괄 저장 (Upsert)"""
        if not statuses:
            return
        for entity in statuses:
            await self._save_status_with_date_records(entity)
        await self.session.flush()

    @override
    async def save_problem_status(self, status: UserProblemStatus) -> None:
        """단일 UserProblemStatus 저장"""
        if not status:
            return
        await self._save_status_with_date_records(status)
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
    async def find_only_banned_problem_by_user_account_id(
        self, user_account_id: UserAccountId
    ) -> UserActivity:
        """밴된 문제만 조회 (banned_yn=true, bj_account_id=NULL)"""
        stmt = select(UserProblemStatusModel).where(
            and_(
                UserProblemStatusModel.user_account_id == user_account_id.value,
                UserProblemStatusModel.banned_yn == True,
                UserProblemStatusModel.deleted_at.is_(None),
            )
        )
        result = await self.session.execute(stmt)
        status_models = result.scalars().all()

        problem_statuses = [
            UserProblemStatusMapper.status_to_entity(model, [])
            for model in status_models
        ]

        return UserActivity(
            user_activity_id=None,
            user_account_id=user_account_id,
            problem_statuses=problem_statuses,
            tag_customizations=[],
        )

    @override
    async def save_problem_banned_record(self, activity: UserActivity) -> None:
        """밴/언밴 문제 저장 (banned_yn 변경, 날짜 레코드 없음)"""
        for entity in activity.problem_statuses:
            existing_status = await self._get_existing_status(
                entity.user_account_id.value,
                entity.problem_id.value,
                entity.bj_account_id  # None for BANNED
            )

            status_model = UserProblemStatusMapper.entity_to_status_model(entity, existing_status)
            if not existing_status:
                self.session.add(status_model)

        await self.session.flush()

    @override
    async def find_problem_records_by_problem_ids(
        self,
        user_id: UserAccountId,
        problem_ids: list[int]
    ) -> list[UserProblemStatus]:
        """특정 문제 ID들의 solved 상태 조회 (활성 BJ 계정)"""
        if not problem_ids:
            return []

        active_bj_id = await self._get_active_bj_account_id(user_id.value)

        stmt = (
            select(UserProblemStatusModel)
            .options(selectinload(UserProblemStatusModel.date_records))
            .where(
                and_(
                    UserProblemStatusModel.user_account_id == user_id.value,
                    UserProblemStatusModel.bj_account_id == active_bj_id,
                    UserProblemStatusModel.problem_id.in_(problem_ids),
                    UserProblemStatusModel.solved_yn == True,
                    UserProblemStatusModel.deleted_at.is_(None)
                )
            )
        )

        result = await self.session.execute(stmt)
        status_models = result.scalars().unique().all()

        statuses = []
        for status_model in status_models:
            active_solved = [
                dr for dr in status_model.date_records
                if dr.record_type == RecordType.SOLVED and dr.deleted_at is None
            ]
            if active_solved:
                statuses.append(UserProblemStatusMapper.status_to_entity(
                    status_model, active_solved
                ))

        return statuses

    @override
    async def find_solved_statuses_by_problem_ids(
        self,
        user_id: UserAccountId,
        problem_ids: list[int]
    ) -> list[UserProblemStatus]:
        """특정 문제 ID들의 solved_yn=True 상태 조회 (date_record 유무 무관)"""
        if not problem_ids:
            return []

        active_bj_id = await self._get_active_bj_account_id(user_id.value)

        stmt = (
            select(UserProblemStatusModel)
            .options(selectinload(UserProblemStatusModel.date_records))
            .where(
                and_(
                    UserProblemStatusModel.user_account_id == user_id.value,
                    UserProblemStatusModel.bj_account_id == active_bj_id,
                    UserProblemStatusModel.problem_id.in_(problem_ids),
                    UserProblemStatusModel.solved_yn == True,
                    UserProblemStatusModel.deleted_at.is_(None)
                )
            )
        )

        result = await self.session.execute(stmt)
        status_models = result.scalars().unique().all()

        return [
            UserProblemStatusMapper.status_to_entity(status_model)
            for status_model in status_models
        ]

    @override
    async def find_will_solve_problems_by_problem_ids(
        self,
        user_id: UserAccountId,
        problem_ids: list[int]
    ) -> list[UserProblemStatus]:
        """특정 문제 ID들의 will_solve 상태 조회 (활성 BJ 계정)"""
        if not problem_ids:
            return []

        active_bj_id = await self._get_active_bj_account_id(user_id.value)

        stmt = (
            select(UserProblemStatusModel)
            .options(selectinload(UserProblemStatusModel.date_records))
            .where(
                and_(
                    UserProblemStatusModel.user_account_id == user_id.value,
                    UserProblemStatusModel.bj_account_id == active_bj_id,
                    UserProblemStatusModel.problem_id.in_(problem_ids),
                    UserProblemStatusModel.solved_yn == False,
                    UserProblemStatusModel.deleted_at.is_(None)
                )
            )
        )

        result = await self.session.execute(stmt)
        status_models = result.scalars().unique().all()

        statuses = []
        for status_model in status_models:
            active_will_solve = [
                dr for dr in status_model.date_records
                if dr.record_type == RecordType.WILL_SOLVE and dr.deleted_at is None
            ]
            if active_will_solve:
                statuses.append(UserProblemStatusMapper.status_to_entity(
                    status_model, active_will_solve
                ))

        return statuses

    @override
    async def find_problem_record_by_problem_id(
        self,
        user_id: UserAccountId,
        problem_id: int
    ) -> UserProblemStatus | None:
        """특정 문제 ID의 solved 상태 조회 (활성 BJ 계정)"""
        active_bj_id = await self._get_active_bj_account_id(user_id.value)

        stmt = (
            select(UserProblemStatusModel)
            .options(selectinload(UserProblemStatusModel.date_records))
            .where(
                and_(
                    UserProblemStatusModel.user_account_id == user_id.value,
                    UserProblemStatusModel.bj_account_id == active_bj_id,
                    UserProblemStatusModel.problem_id == problem_id,
                    UserProblemStatusModel.solved_yn == True,
                    UserProblemStatusModel.deleted_at.is_(None)
                )
            )
        )

        result = await self.session.execute(stmt)
        status_model = result.scalar_one_or_none()

        if not status_model:
            return None

        active_solved = [
            dr for dr in status_model.date_records
            if dr.record_type == RecordType.SOLVED and dr.deleted_at is None
        ]
        if not active_solved:
            return None

        return UserProblemStatusMapper.status_to_entity(status_model, active_solved[:1])

    @override
    async def find_will_solve_problem_by_problem_id(
        self,
        user_id: UserAccountId,
        problem_id: int
    ) -> UserProblemStatus | None:
        """특정 문제 ID의 will_solve 상태 조회 (활성 BJ 계정)"""
        active_bj_id = await self._get_active_bj_account_id(user_id.value)

        stmt = (
            select(UserProblemStatusModel)
            .options(selectinload(UserProblemStatusModel.date_records))
            .where(
                and_(
                    UserProblemStatusModel.user_account_id == user_id.value,
                    UserProblemStatusModel.bj_account_id == active_bj_id,
                    UserProblemStatusModel.problem_id == problem_id,
                    UserProblemStatusModel.solved_yn == False,
                    UserProblemStatusModel.banned_yn == False,
                    UserProblemStatusModel.deleted_at.is_(None)
                )
            )
        )

        result = await self.session.execute(stmt)
        status_model = result.scalar_one_or_none()

        if not status_model:
            return None

        active_will_solve = [
            dr for dr in status_model.date_records
            if dr.record_type == RecordType.WILL_SOLVE and dr.deleted_at is None
        ]
        if not active_will_solve:
            return None

        return UserProblemStatusMapper.status_to_entity(status_model, active_will_solve[:1])

    @override
    async def count_solved_by_date(
        self,
        user_id: UserAccountId,
        bj_account_id: str,
        target_date: date
    ) -> int:
        """특정 날짜의 활성 SOLVED 레코드 수 조회"""
        stmt = (
            select(func.count())
            .select_from(ProblemDateRecordModel)
            .join(
                UserProblemStatusModel,
                ProblemDateRecordModel.user_problem_status_id == UserProblemStatusModel.user_problem_status_id
            )
            .where(
                and_(
                    UserProblemStatusModel.user_account_id == user_id.value,
                    UserProblemStatusModel.bj_account_id == bj_account_id,
                    ProblemDateRecordModel.marked_date == target_date,
                    ProblemDateRecordModel.record_type == RecordType.SOLVED,
                    ProblemDateRecordModel.deleted_at.is_(None)
                )
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar() or 0

    @override
    async def delete_all_by_user_account_id(self, user_account_id: UserAccountId) -> None:
        """사용자와 연관된 모든 활동 데이터 삭제 (Hard Delete)"""
        user_id_value = user_account_id.value

        await self.session.execute(
            delete(TagCustomModel).where(TagCustomModel.user_account_id == user_id_value)
        )

        # user_problem_status 삭제 (CASCADE로 problem_date_record도 삭제됨)
        await self.session.execute(
            delete(UserProblemStatusModel).where(
                UserProblemStatusModel.user_account_id == user_id_value
            )
        )
