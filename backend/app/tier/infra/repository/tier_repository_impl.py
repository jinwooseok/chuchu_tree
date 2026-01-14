"""Tier Repository 구현"""

from typing import override
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.domain.vo.identifiers import TierId
from app.core.database import Database
from app.tier.domain.entity.tier import Tier
from app.tier.domain.repository.tier_repository import TierRepository
from app.tier.infra.mapper.tier_mapper import TierMapper
from app.tier.infra.model.tier import TierModel


class TierRepositoryImpl(TierRepository):
    """Tier Repository 구현체"""

    def __init__(self, db: Database):
        self.db = db

    @property
    def session(self) -> AsyncSession:
        return self.db.get_current_session()

    @override
    async def save(self, tier: Tier) -> Tier:
        """티어 저장"""
        model = TierMapper.to_model(tier)
        self.session.add(model)
        await self.session.flush()
        return TierMapper.to_entity(model)

    @override
    async def find_by_id(self, tier_id: TierId) -> Tier | None:
        """티어 ID로 조회"""
        stmt = select(TierModel).where(
            TierModel.tier_id == tier_id.value
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return TierMapper.to_entity(model) if model else None

    @override
    async def find_by_level(self, tier_level: int) -> Tier | None:
        """티어 레벨로 조회"""
        stmt = select(TierModel).where(
            TierModel.tier_level == tier_level
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return TierMapper.to_entity(model) if model else None

    @override
    async def find_by_code(self, tier_code: str) -> Tier | None:
        """티어 코드로 조회"""
        stmt = select(TierModel).where(
            TierModel.tier_code == tier_code
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return TierMapper.to_entity(model) if model else None

    @override
    async def find_all(self) -> list[Tier]:
        """모든 티어 조회"""
        stmt = select(TierModel)
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [TierMapper.to_entity(model) for model in models]
    
    @override
    async def find_by_levels(self, tier_levels: list[int]) -> list[Tier]:
        """여러 티어 레벨로 한 번에 조회 (IN 절 사용)"""
        if not tier_levels:
            return []

        # 중복 제거 (필요한 경우)
        unique_levels = list(set(tier_levels))

        stmt = select(TierModel).where(
            TierModel.tier_level.in_(unique_levels)
        )
        
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        
        return [TierMapper.to_entity(model) for model in models]