"""UserActivity Repository 구현 - 정규화된 테이블 구조"""
from calendar import monthrange
from datetime import date
from typing import override

from sqlalchemy import and_, delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.activity.domain.entity.problem_banned_record import ProblemBannedRecord
from app.activity.domain.entity.problem_record import ProblemRecord
from app.activity.domain.entity.user_activity import UserActivity
from app.activity.domain.entity.will_solve_problem import WillSolveProblem
from app.activity.domain.repository.user_activity_repository import UserActivityRepository
from app.activity.infra.mapper.problem_record_mapper import ProblemRecordMapper
from app.activity.infra.mapper.tag_customization_mapper import TagCustomizationMapper
from app.activity.infra.mapper.user_activity_mapper import UserActivityMapper
from app.activity.infra.model.user_problem_status import UserProblemStatusModel
from app.activity.infra.model.problem_date_record import ProblemDateRecordModel, RecordType
from app.activity.infra.model.tag_custom import TagCustomModel
from app.common.domain.vo.identifiers import UserAccountId
from app.core.database import Database
from app.user.infra.model.user_account import UserAccountModel


class UserActivityRepositoryImpl(UserActivityRepository):
    """UserActivity Repository 구현체

    정규화된 테이블 구조:
    - UserProblemStatusModel: 문제별 마스터 (1:N의 1)
    - ProblemDateRecordModel: 날짜별 디테일 (1:N의 N)

    도메인 엔티티 매핑:
    - SOLVED: solved_yn=true + record_type='SOLVED'
    - WILL_SOLVE: solved_yn=false, banned_yn=false + record_type='WILL_SOLVE'
    - BANNED: banned_yn=true (날짜 레코드 없음)
    """

    def __init__(self, db: Database):
        self.db = db

    @property
    def session(self) -> AsyncSession:
        return self.db.get_current_session()

    @override
    async def find_by_user_account_id(
        self, user_account_id: UserAccountId
    ) -> UserActivity:
        """유저의 모든 활동 데이터를 한 번에 로드"""
        stmt = (
            select(UserAccountModel)
            .options(
                selectinload(UserAccountModel.tag_customs.and_(TagCustomModel.deleted_at.is_(None))),
                selectinload(
                    UserAccountModel.problem_statuses.and_(UserProblemStatusModel.deleted_at.is_(None))
                ).selectinload(
                    UserProblemStatusModel.date_records.and_(ProblemDateRecordModel.deleted_at.is_(None))
                )
            )
            .where(UserAccountModel.user_account_id == user_account_id.value)
        )

        result = await self.session.execute(stmt)
        user_account_model = result.scalar_one_or_none()

        return UserActivityMapper.to_entity(
            user_account_id=user_account_model.user_account_id,
            tag_custom_models=user_account_model.tag_customs,
            problem_status_models=user_account_model.problem_statuses
        )

    @override
    async def find_monthly_problem_records(
        self,
        user_id: UserAccountId,
        year: int,
        month: int
    ) -> list[ProblemRecord]:
        """월간 푼 문제 기록 조회 (solved_yn=true, record_type='SOLVED')"""
        _, last_day = monthrange(year, month)
        start_date = date(year, month, 1)
        end_date = date(year, month, last_day)

        stmt = (
            select(UserProblemStatusModel)
            .join(ProblemDateRecordModel)
            .options(selectinload(UserProblemStatusModel.date_records))
            .where(
                and_(
                    UserProblemStatusModel.user_account_id == user_id.value,
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
        statuses = result.scalars().unique().all()

        records = []
        for status in statuses:
            for date_record in status.date_records:
                if (date_record.record_type == RecordType.SOLVED and
                    date_record.deleted_at is None and
                    start_date <= date_record.marked_date <= end_date):
                    records.append(ProblemRecordMapper.to_entity(status, date_record))

        return sorted(records, key=lambda r: r.marked_date)

    @override
    async def find_monthly_will_solve_problems(
        self,
        user_id: UserAccountId,
        year: int,
        month: int
    ) -> list[WillSolveProblem]:
        """월간 풀 예정 문제 조회 (solved_yn=false, banned_yn=false, record_type='WILL_SOLVE')"""
        _, last_day = monthrange(year, month)
        start_date = date(year, month, 1)
        end_date = date(year, month, last_day)

        stmt = (
            select(UserProblemStatusModel)
            .join(ProblemDateRecordModel)
            .options(selectinload(UserProblemStatusModel.date_records))
            .where(
                and_(
                    UserProblemStatusModel.user_account_id == user_id.value,
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
        statuses = result.scalars().unique().all()

        records = []
        for status in statuses:
            for date_record in status.date_records:
                if (date_record.record_type == RecordType.WILL_SOLVE and
                    date_record.deleted_at is None and
                    start_date <= date_record.marked_date <= end_date):
                    records.append(ProblemRecordMapper.to_will_solve_entity(status, date_record))

        return sorted(records, key=lambda r: (r.marked_date, r.order))

    @override
    async def find_will_solve_problems_by_date(
        self,
        user_id: UserAccountId,
        target_date: date
    ) -> list[WillSolveProblem]:
        """날짜별 풀 예정 문제 조회 (solved_yn=false, banned_yn=false, record_type='WILL_SOLVE')"""
        stmt = (
            select(UserProblemStatusModel)
            .join(ProblemDateRecordModel)
            .options(selectinload(UserProblemStatusModel.date_records))
            .where(
                and_(
                    UserProblemStatusModel.user_account_id == user_id.value,
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
        statuses = result.scalars().unique().all()

        records = []
        for status in statuses:
            for date_record in status.date_records:
                if (date_record.record_type == RecordType.WILL_SOLVE and
                    date_record.deleted_at is None and
                    date_record.marked_date == target_date):
                    records.append(ProblemRecordMapper.to_will_solve_entity(status, date_record))

        return sorted(records, key=lambda r: r.order)

    @override
    async def find_problem_records_by_date(
        self,
        user_id: UserAccountId,
        target_date: date
    ) -> list[ProblemRecord]:
        """날짜별 푼 문제 조회 (solved_yn=true, record_type='SOLVED')"""
        stmt = (
            select(UserProblemStatusModel)
            .join(ProblemDateRecordModel)
            .options(selectinload(UserProblemStatusModel.date_records))
            .where(
                and_(
                    UserProblemStatusModel.user_account_id == user_id.value,
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
        statuses = result.scalars().unique().all()

        records = []
        for status in statuses:
            for date_record in status.date_records:
                if (date_record.record_type == RecordType.SOLVED and
                    date_record.deleted_at is None and
                    date_record.marked_date == target_date):
                    records.append(ProblemRecordMapper.to_entity(status, date_record))

        return sorted(records, key=lambda r: r.order)

    async def _get_or_create_status(
        self,
        user_account_id: int,
        problem_id: int
    ) -> UserProblemStatusModel:
        """기존 status 조회 또는 새로 생성"""
        stmt = select(UserProblemStatusModel).where(
            and_(
                UserProblemStatusModel.user_account_id == user_account_id,
                UserProblemStatusModel.problem_id == problem_id
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    @override
    async def save_all_will_solve_problems(
        self,
        will_solve_problems: list[WillSolveProblem]
    ) -> None:
        """일괄 저장 및 업데이트 (Upsert) - 2개 테이블 처리"""
        if not will_solve_problems:
            return

        for entity in will_solve_problems:
            # 1. Status 조회 또는 생성
            existing_status = await self._get_or_create_status(
                entity.user_account_id.value,
                entity.problem_id.value
            )

            if existing_status:
                # 기존 status 업데이트
                status_model = ProblemRecordMapper.from_will_solve_to_status_model(
                    entity, existing_status
                )
            else:
                # 새 status 생성
                status_model = ProblemRecordMapper.from_will_solve_to_status_model(entity)
                self.session.add(status_model)
                await self.session.flush()

            # 2. Date record 처리
            if entity.will_solve_problem_id:
                # 기존 date record 조회
                date_stmt = select(ProblemDateRecordModel).where(
                    ProblemDateRecordModel.problem_date_record_id == entity.will_solve_problem_id
                )
                date_result = await self.session.execute(date_stmt)
                existing_date_record = date_result.scalar_one_or_none()

                date_record = ProblemRecordMapper.from_will_solve_to_date_record(
                    entity, status_model.user_problem_status_id, existing_date_record
                )
                if not existing_date_record:
                    self.session.add(date_record)
            else:
                date_record = ProblemRecordMapper.from_will_solve_to_date_record(
                    entity, status_model.user_problem_status_id
                )
                self.session.add(date_record)

        await self.session.flush()

    @override
    async def save_all_problem_records(
        self,
        problem_records: list[ProblemRecord]
    ) -> None:
        """일괄 저장 및 업데이트 (Upsert) - 2개 테이블 처리"""
        if not problem_records:
            return

        for entity in problem_records:
            # 1. Status 조회 또는 생성
            existing_status = await self._get_or_create_status(
                entity.user_account_id.value,
                entity.problem_id.value
            )

            if existing_status:
                status_model = ProblemRecordMapper.to_status_model(entity, existing_status)
            else:
                status_model = ProblemRecordMapper.to_status_model(entity)
                self.session.add(status_model)
                await self.session.flush()

            # 2. Date record 처리
            if entity.problem_record_id:
                date_stmt = select(ProblemDateRecordModel).where(
                    ProblemDateRecordModel.problem_date_record_id == entity.problem_record_id
                )
                date_result = await self.session.execute(date_stmt)
                existing_date_record = date_result.scalar_one_or_none()

                date_record = ProblemRecordMapper.to_date_record_model(
                    entity, status_model.user_problem_status_id, existing_date_record
                )
                if not existing_date_record:
                    self.session.add(date_record)
            else:
                date_record = ProblemRecordMapper.to_date_record_model(
                    entity, status_model.user_problem_status_id
                )
                self.session.add(date_record)

        await self.session.flush()

    @override
    async def save_problem_record(
        self,
        problem_record: ProblemRecord
    ) -> None:
        """저장 및 업데이트 (Upsert) - 2개 테이블 처리"""
        if not problem_record:
            return

        await self.save_all_problem_records([problem_record])

    @override
    async def save_will_solve_problem(
        self,
        will_solve_problem: WillSolveProblem
    ) -> None:
        """저장 및 업데이트 (Upsert) - 2개 테이블 처리"""
        if not will_solve_problem:
            return

        await self.save_all_will_solve_problems([will_solve_problem])

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
        """밴된 문제만 조회 (banned_yn=true)"""
        stmt = select(UserProblemStatusModel).where(
            and_(
                UserProblemStatusModel.user_account_id == user_account_id.value,
                UserProblemStatusModel.banned_yn == True,
                UserProblemStatusModel.deleted_at.is_(None),
            )
        )
        result = await self.session.execute(stmt)
        status_models = result.scalars().all()

        banned_problems = [ProblemRecordMapper.to_banned_entity(model) for model in status_models]

        return UserActivity(
            user_activity_id=None,
            user_account_id=user_account_id,
            will_solve_problems=[],
            banned_problems=banned_problems,
            solved_problems=[],
            tag_customizations=[],
        )

    @override
    async def save_problem_banned_record(self, activity: UserActivity):
        """밴된 문제 저장 (banned_yn=true로 저장, 날짜 레코드 없음)"""
        if not activity.banned_problems:
            return

        for entity in activity.banned_problems:
            existing_status = await self._get_or_create_status(
                entity.user_account_id.value,
                entity.problem_id.value
            )

            if existing_status:
                status_model = ProblemRecordMapper.from_banned_to_status_model(
                    entity, existing_status
                )
            else:
                status_model = ProblemRecordMapper.from_banned_to_status_model(entity)
                self.session.add(status_model)

        await self.session.flush()

    @override
    async def find_problem_records_by_problem_ids(
        self,
        user_id: UserAccountId,
        problem_ids: list[int]
    ) -> list[ProblemRecord]:
        """특정 문제 ID들의 problem_record 조회 (solved_yn=true, record_type='SOLVED')"""
        if not problem_ids:
            return []

        stmt = (
            select(UserProblemStatusModel)
            .options(selectinload(UserProblemStatusModel.date_records))
            .where(
                and_(
                    UserProblemStatusModel.user_account_id == user_id.value,
                    UserProblemStatusModel.problem_id.in_(problem_ids),
                    UserProblemStatusModel.solved_yn == True,
                    UserProblemStatusModel.deleted_at.is_(None)
                )
            )
        )

        result = await self.session.execute(stmt)
        statuses = result.scalars().unique().all()

        records = []
        for status in statuses:
            for date_record in status.date_records:
                if (date_record.record_type == RecordType.SOLVED and
                    date_record.deleted_at is None):
                    records.append(ProblemRecordMapper.to_entity(status, date_record))

        return records

    @override
    async def find_will_solve_problems_by_problem_ids(
        self,
        user_id: UserAccountId,
        problem_ids: list[int]
    ) -> list[WillSolveProblem]:
        """특정 문제 ID들의 will_solve_problem 조회 (solved_yn=false=)"""
        if not problem_ids:
            return []

        stmt = (
            select(UserProblemStatusModel)
            .options(selectinload(UserProblemStatusModel.date_records))
            .where(
                and_(
                    UserProblemStatusModel.user_account_id == user_id.value,
                    UserProblemStatusModel.problem_id.in_(problem_ids),
                    UserProblemStatusModel.solved_yn == False,
                    UserProblemStatusModel.deleted_at.is_(None)
                )
            )
        )

        result = await self.session.execute(stmt)
        statuses = result.scalars().unique().all()

        records = []
        for status in statuses:
            for date_record in status.date_records:
                if (date_record.record_type == RecordType.WILL_SOLVE and
                    date_record.deleted_at is None):
                    records.append(ProblemRecordMapper.to_will_solve_entity(status, date_record))

        return records

    @override
    async def find_problem_record_by_problem_id(
        self,
        user_id: UserAccountId,
        problem_id: int
    ) -> ProblemRecord | None:
        """특정 문제 ID의 problem_record 조회 (solved_yn=true)"""
        stmt = (
            select(UserProblemStatusModel)
            .options(selectinload(UserProblemStatusModel.date_records))
            .where(
                and_(
                    UserProblemStatusModel.user_account_id == user_id.value,
                    UserProblemStatusModel.problem_id == problem_id,
                    UserProblemStatusModel.solved_yn == True,
                    UserProblemStatusModel.deleted_at.is_(None)
                )
            )
        )

        result = await self.session.execute(stmt)
        status = result.scalar_one_or_none()

        if not status:
            return None

        for date_record in status.date_records:
            if (date_record.record_type == RecordType.SOLVED and
                date_record.deleted_at is None):
                return ProblemRecordMapper.to_entity(status, date_record)

        return None

    @override
    async def find_will_solve_problem_by_problem_id(
        self,
        user_id: UserAccountId,
        problem_id: int
    ) -> WillSolveProblem | None:
        """특정 문제 ID의 will_solve_problem 조회 (solved_yn=false, banned_yn=false)"""
        stmt = (
            select(UserProblemStatusModel)
            .options(selectinload(UserProblemStatusModel.date_records))
            .where(
                and_(
                    UserProblemStatusModel.user_account_id == user_id.value,
                    UserProblemStatusModel.problem_id == problem_id,
                    UserProblemStatusModel.solved_yn == False,
                    UserProblemStatusModel.banned_yn == False,
                    UserProblemStatusModel.deleted_at.is_(None)
                )
            )
        )

        result = await self.session.execute(stmt)
        status = result.scalar_one_or_none()

        if not status:
            return None

        for date_record in status.date_records:
            if (date_record.record_type == RecordType.WILL_SOLVE and
                date_record.deleted_at is None):
                return ProblemRecordMapper.to_will_solve_entity(status, date_record)

        return None

    @override
    async def delete_all_by_user_account_id(self, user_account_id: UserAccountId) -> None:
        """
        사용자와 연관된 모든 활동 데이터 삭제 (Hard Delete)
        - tag_custom
        - user_problem_status (CASCADE로 problem_date_record도 삭제)
        """
        user_id_value = user_account_id.value

        # 1. tag_custom 삭제
        await self.session.execute(
            delete(TagCustomModel).where(TagCustomModel.user_account_id == user_id_value)
        )

        # 2. user_problem_status 삭제 (CASCADE로 problem_date_record도 삭제됨)
        await self.session.execute(
            delete(UserProblemStatusModel).where(
                UserProblemStatusModel.user_account_id == user_id_value
            )
        )
