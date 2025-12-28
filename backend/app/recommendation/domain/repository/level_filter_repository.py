from abc import ABCMeta, abstractmethod

from app.common.domain.enums import FilterCode
from app.common.domain.vo.identifiers import LevelFilterId
from app.recommendation.domain.entity.level_filter import LevelFilter


class LevelFilterRepository(ABCMeta):
    """Repository 인터페이스"""
    
    @abstractmethod
    async def save(self, filter: LevelFilter) -> LevelFilter:
        pass
    
    @abstractmethod
    async def find_by_id(self, filter_id: LevelFilterId) -> LevelFilter | None:
        pass
    
    @abstractmethod
    async def find_by_code(self, code: FilterCode) -> LevelFilter | None:
        pass
    
    @abstractmethod
    async def find_all_active(self) -> list[LevelFilter]:
        pass