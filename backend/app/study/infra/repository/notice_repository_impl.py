from sqlalchemy import and_, delete, func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.domain.vo.identifiers import UserAccountId
from app.core.database import Database
from app.study.domain.entity.notice import Notice
from app.study.domain.repository.notice_repository import NoticeRepository
from app.study.infra.mapper.notice_mapper import NoticeMapper
from app.study.infra.model.notice import NoticeModel


class NoticeRepositoryImpl(NoticeRepository):
    def __init__(self, db: Database):
        self.db = db

    @property
    def session(self) -> AsyncSession:
        return self.db.get_current_session()

    async def insert(self, notice: Notice) -> Notice:
        model = NoticeMapper.to_model(notice)
        self.session.add(model)
        await self.session.flush()
        return NoticeMapper.to_entity(model)

    async def find_by_id(self, notice_id: int) -> Notice | None:
        stmt = select(NoticeModel).where(
            and_(
                NoticeModel.notice_id == notice_id,
                NoticeModel.deleted_at.is_(None),
            )
        )
        result = await self.session.execute(stmt)
        model = result.scalars().one_or_none()
        return NoticeMapper.to_entity(model) if model else None

    async def insert_many(self, notices: list[Notice]) -> list[Notice]:
        models = [NoticeMapper.to_model(n) for n in notices]
        for model in models:
            self.session.add(model)
        await self.session.flush()
        return [NoticeMapper.to_entity(m) for m in models]

    async def find_by_recipient(
        self, user_account_id: UserAccountId, limit: int = 50
    ) -> list[Notice]:
        stmt = (
            select(NoticeModel)
            .where(
                and_(
                    NoticeModel.recipient_user_account_id == user_account_id.value,
                    NoticeModel.deleted_at.is_(None),
                )
            )
            .order_by(NoticeModel.created_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [NoticeMapper.to_entity(m) for m in models]

    async def find_unread_count_by_recipient(self, user_account_id: UserAccountId) -> int:
        stmt = select(func.count(NoticeModel.notice_id)).where(
            and_(
                NoticeModel.recipient_user_account_id == user_account_id.value,
                NoticeModel.is_read == False,
                NoticeModel.deleted_at.is_(None),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one() or 0

    async def update(self, notice: Notice) -> Notice:
        model = NoticeMapper.to_model(notice)
        merged = await self.session.merge(model)
        await self.session.flush()
        return NoticeMapper.to_entity(merged)

    async def delete_all_by_user_account_id(self, user_account_id: UserAccountId) -> None:
        stmt = delete(NoticeModel).where(
            NoticeModel.recipient_user_account_id == user_account_id.value
        )
        await self.session.execute(stmt)
        await self.session.flush()

    async def mark_all_read_by_recipient(self, user_account_id: UserAccountId) -> None:
        from datetime import datetime
        stmt = (
            update(NoticeModel)
            .where(
                and_(
                    NoticeModel.recipient_user_account_id == user_account_id.value,
                    NoticeModel.is_read == False,
                    NoticeModel.deleted_at.is_(None),
                )
            )
            .values(is_read=True, updated_at=datetime.now())
        )
        await self.session.execute(stmt)
        await self.session.flush()
