"""Tag Repository 구현"""
from typing import override

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.common.domain.enums import TagLevel
from app.common.domain.vo.identifiers import TagId
from app.core.database import Database
from app.tag.domain.entity.tag import Tag
from app.tag.domain.repository.tag_repository import TagRepository
from app.tag.infra.mapper.tag_mapper import TagMapper
from app.tag.infra.model.tag import TagModel


class TagRepositoryImpl(TagRepository):
    """Tag Repository 구현체"""

    def __init__(self, db: Database):
        self.db = db

    @property
    def session(self) -> AsyncSession:
        return self.db.get_current_session()

    @override
    async def save(self, tag: Tag) -> Tag:
        """태그 저장"""
        model = TagMapper.to_model(tag)
        self.session.add(model)
        await self.session.flush()
        return TagMapper.to_entity(model)

    @override
    async def find_by_id(self, tag_id: TagId) -> Tag | None:
        """태그 ID로 조회"""
        stmt = (
            select(TagModel)
            .options(joinedload(TagModel.parent_tag_relations))
            .where(
                and_(
                    TagModel.tag_id == tag_id.value,
                    TagModel.deleted_at.is_(None)
                )
            )
        )
        result = await self.session.execute(stmt)
        model = result.unique().scalars().one_or_none()
        return TagMapper.to_entity(model) if model else None

    @override
    async def find_by_ids(self, tag_ids: list[TagId]) -> list[Tag]:
        """여러 ID로 조회"""
        if not tag_ids:
            return []

        tag_id_values = [tid.value for tid in tag_ids]
        stmt = (
            select(TagModel)
            .options(joinedload(TagModel.parent_tag_relations))
            .where(
                and_(
                    TagModel.tag_id.in_(tag_id_values),
                    TagModel.deleted_at.is_(None)
                )
            )
        )

        result = await self.session.execute(stmt)
        models = result.unique().scalars().fetchall()

        return [TagMapper.to_entity(model) for model in models]
    
    @override
    async def find_by_ids_and_active(self, tag_ids: list[TagId]) -> list[Tag]:
        """여러 ID로 조회"""
        if not tag_ids:
            return []

        tag_id_values = [tid.value for tid in tag_ids]
        stmt = (
            select(TagModel)
            .options(joinedload(TagModel.parent_tag_relations))
            .where(
                and_(
                    TagModel.tag_id.in_(tag_id_values),
                    TagModel.deleted_at.is_(None)
                )
            )
        )

        result = await self.session.execute(stmt)
        models = result.unique().scalars().fetchall()

        return [TagMapper.to_entity(model) for model in models]
    
    @override
    async def find_by_code(self, code: str) -> Tag | None:
        """코드로 조회"""
        stmt = (
            select(TagModel)
            .options(joinedload(TagModel.parent_tag_relations))
            .where(
                and_(
                    TagModel.tag_code == code,
                    TagModel.deleted_at.is_(None)
                )
            )
        )
        result = await self.session.execute(stmt)
        model = result.unique().scalars().one_or_none()
        return TagMapper.to_entity(model) if model else None

    @override
    async def find_by_level(self, level: TagLevel) -> list[Tag]:
        """레벨로 조회"""
        stmt = (
            select(TagModel)
            .options(joinedload(TagModel.parent_tag_relations))
            .where(
                and_(
                    TagModel.tag_level == level.value,
                    TagModel.deleted_at.is_(None)
                )
            )
            .order_by(TagModel.tag_id.asc())
        )
        result = await self.session.execute(stmt)
        models = result.unique().scalars().fetchall()
        return [TagMapper.to_entity(model) for model in models]

    @override
    async def find_active_tags(self) -> list[Tag]:
        """활성 태그 조회"""
        stmt = (
            select(TagModel)
            .options(joinedload(TagModel.parent_tag_relations))
            .where(
                and_(
                    TagModel.excluded_yn == False,
                    TagModel.deleted_at.is_(None)
                )
            )
            .order_by(TagModel.tag_id.asc())
        )
        result = await self.session.execute(stmt)
        models = result.unique().scalars().fetchall()
        return [TagMapper.to_entity(model) for model in models]
