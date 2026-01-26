from abc import ABC, abstractmethod

from app.common.domain.enums import FilterCode, SkillCode, TagLevel
from app.common.domain.vo.identifiers import LevelFilterId, TagSkillId
from app.recommendation.domain.entity.level_filter import LevelFilter
from app.recommendation.domain.entity.tag_skill import TagSkill


class LevelFilterRepository(ABC):
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

    @abstractmethod
    async def find_by_skill_and_code(
        self,
        tag_skill_level: str,
        filter_code: str
    ) -> LevelFilter | None:
        pass