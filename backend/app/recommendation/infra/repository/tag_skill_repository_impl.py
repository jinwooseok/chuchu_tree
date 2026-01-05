"""TagSkill Repository 구현"""

from typing import override
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.domain.enums import SkillCode, TagLevel
from app.common.domain.vo.identifiers import TagSkillId
from app.core.database import Database
from app.recommendation.domain.entity.tag_skill import TagSkill
from app.recommendation.domain.repository.tag_skill_repository import TagSkillRepository
from app.recommendation.infra.mapper.tag_skill_mapper import TagSkillMapper
from app.recommendation.infra.model.tag_skill import TagSkillModel


class TagSkillRepositoryImpl(TagSkillRepository):
    """TagSkill Repository 구현체"""

    def __init__(self, db: Database):
        self.db = db

    @property
    def session(self) -> AsyncSession:
        return self.db.get_current_session()

    @override
    async def save(self, tag_skill: TagSkill) -> TagSkill:
        """TagSkill 저장"""
        model = TagSkillMapper.to_model(tag_skill)
        self.session.add(model)
        await self.session.flush()
        return TagSkillMapper.to_entity(model)

    @override
    async def find_by_id(self, skill_id: TagSkillId) -> TagSkill | None:
        """ID로 TagSkill 조회"""
        stmt = select(TagSkillModel).where(
            and_(
                TagSkillModel.tag_skill_id == skill_id.value,
                TagSkillModel.deleted_at.is_(None)
            )
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return TagSkillMapper.to_entity(model)

    @override
    async def find_by_level_and_code(
        self,
        level: TagLevel,
        code: SkillCode
    ) -> TagSkill | None:
        """태그 레벨과 스킬 코드로 조회"""
        stmt = select(TagSkillModel).where(
            and_(
                TagSkillModel.tag_level == level.value,
                TagSkillModel.tag_skill_code == code.value,
                TagSkillModel.active_yn == True,
                TagSkillModel.deleted_at.is_(None)
            )
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return TagSkillMapper.to_entity(model)

    @override
    async def find_all_active(self) -> list[TagSkill]:
        """모든 활성 TagSkill 조회"""
        stmt = select(TagSkillModel).where(
            and_(
                TagSkillModel.active_yn == True,
                TagSkillModel.deleted_at.is_(None)
            )
        )
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [TagSkillMapper.to_entity(model) for model in models]
