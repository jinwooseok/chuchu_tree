"""UserDateRecord Repository 구현"""

from datetime import date, datetime
from typing import override

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.activity.domain.entity.user_date_record import UserDateRecord
from app.activity.domain.repository.user_date_record_repository import UserDateRecordRepository
from app.activity.infra.model.user_date_record import UserDateRecordModel
from app.common.domain.vo.identifiers import UserAccountId, UserDateRecordId
from app.core.database import Database


class UserDateRecordRepositoryImpl(UserDateRecordRepository):
    """유저 날짜별 풀이 수 Repository 구현체"""

    def __init__(self, db: Database):
        self.db = db

    @property
    def session(self) -> AsyncSession:
        return self.db.get_current_session()

    def _to_entity(self, model: UserDateRecordModel) -> UserDateRecord:
        return UserDateRecord(
            user_date_record_id=UserDateRecordId(model.user_date_record_id),
            user_account_id=UserAccountId(model.user_account_id),
            bj_account_id=model.bj_account_id,
            marked_date=model.marked_date,
            solved_count=model.solved_count,
            created_at=model.created_at,
            updated_at=model.updated_at
        )

    @override
    async def find_by_user_and_date_range(
        self,
        user_account_id: UserAccountId,
        bj_account_id: str,
        start_date: date,
        end_date: date
    ) -> list[UserDateRecord]:
        stmt = (
            select(UserDateRecordModel)
            .where(
                and_(
                    UserDateRecordModel.user_account_id == user_account_id.value,
                    UserDateRecordModel.bj_account_id == bj_account_id,
                    UserDateRecordModel.marked_date >= start_date,
                    UserDateRecordModel.marked_date <= end_date
                )
            )
            .order_by(UserDateRecordModel.marked_date.asc())
        )
        result = await self.session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()]

    @override
    async def find_by_user_and_date(
        self,
        user_account_id: UserAccountId,
        bj_account_id: str,
        target_date: date
    ) -> UserDateRecord | None:
        stmt = select(UserDateRecordModel).where(
            and_(
                UserDateRecordModel.user_account_id == user_account_id.value,
                UserDateRecordModel.bj_account_id == bj_account_id,
                UserDateRecordModel.marked_date == target_date
            )
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    @override
    async def upsert(self, record: UserDateRecord) -> UserDateRecord:
        existing = await self.find_by_user_and_date(
            record.user_account_id, record.bj_account_id, record.marked_date
        )
        if existing:
            stmt = select(UserDateRecordModel).where(
                UserDateRecordModel.user_date_record_id == existing.user_date_record_id.value
            )
            result = await self.session.execute(stmt)
            model = result.scalar_one()
            model.solved_count = record.solved_count
            model.updated_at = datetime.now()
            await self.session.flush()
            return self._to_entity(model)
        else:
            model = UserDateRecordModel(
                user_account_id=record.user_account_id.value,
                bj_account_id=record.bj_account_id,
                marked_date=record.marked_date,
                solved_count=record.solved_count,
                created_at=record.created_at,
                updated_at=record.updated_at
            )
            self.session.add(model)
            await self.session.flush()
            return self._to_entity(model)

    @override
    async def upsert_increment(
        self,
        user_account_id: UserAccountId,
        bj_account_id: str,
        target_date: date,
        increment: int
    ) -> UserDateRecord:
        """solved_count를 increment만큼 증가시키는 UPSERT"""
        existing = await self.find_by_user_and_date(user_account_id, bj_account_id, target_date)
        if existing:
            stmt = select(UserDateRecordModel).where(
                UserDateRecordModel.user_date_record_id == existing.user_date_record_id.value
            )
            result = await self.session.execute(stmt)
            model = result.scalar_one()
            model.solved_count += increment
            model.updated_at = datetime.now()
            await self.session.flush()
            return self._to_entity(model)
        else:
            now = datetime.now()
            model = UserDateRecordModel(
                user_account_id=user_account_id.value,
                bj_account_id=bj_account_id,
                marked_date=target_date,
                solved_count=increment,
                created_at=now,
                updated_at=now
            )
            self.session.add(model)
            await self.session.flush()
            return self._to_entity(model)

    @override
    async def save_all(self, records: list[UserDateRecord]) -> None:
        """여러 기록 일괄 저장 (신규만, 중복 skip)"""
        if not records:
            return

        keys = [(r.user_account_id.value, r.bj_account_id, r.marked_date) for r in records]
        stmt = select(UserDateRecordModel).where(
            and_(
                UserDateRecordModel.user_account_id.in_([k[0] for k in keys]),
                UserDateRecordModel.bj_account_id.in_([k[1] for k in keys]),
                UserDateRecordModel.marked_date.in_([k[2] for k in keys])
            )
        )
        result = await self.session.execute(stmt)
        existing_keys = {
            (m.user_account_id, m.bj_account_id, m.marked_date)
            for m in result.scalars().all()
        }

        new_models = []
        for record in records:
            key = (record.user_account_id.value, record.bj_account_id, record.marked_date)
            if key not in existing_keys:
                new_models.append(UserDateRecordModel(
                    user_account_id=record.user_account_id.value,
                    bj_account_id=record.bj_account_id,
                    marked_date=record.marked_date,
                    solved_count=record.solved_count,
                    created_at=record.created_at,
                    updated_at=record.updated_at
                ))

        if new_models:
            self.session.add_all(new_models)
            await self.session.flush()
