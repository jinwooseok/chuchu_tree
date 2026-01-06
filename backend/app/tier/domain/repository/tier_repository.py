from abc import ABC, abstractmethod

from app.common.domain.vo.identifiers import TierId
from app.tier.domain.entity.tier import Tier


class TierRepository(ABC):
    """Repository 인터페이스"""
    
    @abstractmethod
    async def save(self, tier: Tier) -> Tier:
        pass
    
    @abstractmethod
    async def find_by_id(self, tier_id: TierId) -> Tier | None:
        pass
    
    @abstractmethod
    async def find_by_level(self, tier_level: int) -> Tier | None:
        pass
    
    @abstractmethod
    async def find_by_levels(self, tier_levels: list[int]) -> list[Tier]:
        pass
    
    @abstractmethod
    async def find_by_code(self, tier_code: str) -> Tier | None:
        pass
    
    @abstractmethod
    async def find_all(self) -> list[Tier]:
        pass