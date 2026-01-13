"""LevelFilter Repository 구현"""

from typing import override
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.domain.enums import FilterCode, SkillCode, TagLevel
from app.common.domain.vo.identifiers import LevelFilterId, TagSkillId
from app.core.database import Database
from app.recommendation.domain.entity.level_filter import LevelFilter
from app.recommendation.domain.entity.tag_skill import TagSkill
from app.recommendation.domain.repository.level_filter_repository import LevelFilterRepository
from app.recommendation.infra.mapper.level_filter_mapper import LevelFilterMapper
from app.recommendation.infra.model.problem_recommendation_level_filter import ProblemRecommendationLevelFilterModel


class LevelFilterRepositoryImpl(LevelFilterRepository):
    """LevelFilter Repository 구현체"""

    def __init__(self, db: Database):
        self.db = db

    @property
    def session(self) -> AsyncSession:
        return self.db.get_current_session()

    @override
    async def save(self, filter: LevelFilter) -> LevelFilter:
        """LevelFilter 저장"""
        model = LevelFilterMapper.to_model(filter)
        self.session.add(model)
        await self.session.flush()
        return LevelFilterMapper.to_entity(model)

    @override
    async def find_by_id(self, filter_id: LevelFilterId) -> LevelFilter | None:
        """ID로 LevelFilter 조회"""
        stmt = select(ProblemRecommendationLevelFilterModel).where(
            and_(
                ProblemRecommendationLevelFilterModel.filter_id == filter_id.value,
                ProblemRecommendationLevelFilterModel.deleted_at.is_(None)
            )
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return LevelFilterMapper.to_entity(model)

    @override
    async def find_by_code(self, code: FilterCode) -> LevelFilter | None:
        """필터 코드로 조회"""
        stmt = select(ProblemRecommendationLevelFilterModel).where(
            and_(
                ProblemRecommendationLevelFilterModel.filter_code == code.value,
                ProblemRecommendationLevelFilterModel.active_yn == True,
                ProblemRecommendationLevelFilterModel.deleted_at.is_(None)
            )
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return LevelFilterMapper.to_entity(model)

    @override
    async def find_all_active(self) -> list[LevelFilter]:
        """모든 활성 LevelFilter 조회"""
        stmt = select(ProblemRecommendationLevelFilterModel).where(
            and_(
                ProblemRecommendationLevelFilterModel.active_yn == True,
                ProblemRecommendationLevelFilterModel.deleted_at.is_(None)
            )
        )
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [LevelFilterMapper.to_entity(model) for model in models]

    @override
    async def find_by_skill_and_code(
        self,
        tag_skill_level: str,
        filter_code: str
    ) -> LevelFilter | None:
        """태그 스킬 ID와 필터 코드로 조회"""
        stmt = select(ProblemRecommendationLevelFilterModel).where(
            and_(
                ProblemRecommendationLevelFilterModel.tag_skill_code == tag_skill_level,
                ProblemRecommendationLevelFilterModel.filter_code == filter_code,
                ProblemRecommendationLevelFilterModel.active_yn == True,
                ProblemRecommendationLevelFilterModel.deleted_at.is_(None)
            )
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return LevelFilterMapper.to_entity(model)
