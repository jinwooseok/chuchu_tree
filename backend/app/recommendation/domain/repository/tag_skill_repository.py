from abc import ABC, abstractmethod

from app.common.domain.enums import SkillCode, TagLevel
from app.common.domain.vo.identifiers import TagSkillId
from app.recommendation.domain.entity.tag_skill import TagSkill


class TagSkillRepository(ABC):
    """Repository 인터페이스"""
    
    @abstractmethod
    async def save(self, tag_skill: TagSkill) -> TagSkill:
        pass
    
    @abstractmethod
    async def find_by_id(self, skill_id: TagSkillId) -> TagSkill | None:
        pass
    
    @abstractmethod
    async def find_by_level_and_code(
        self,
        level: TagLevel,
        code: SkillCode
    ) -> TagSkill | None:
        pass
    
    @abstractmethod
    async def find_all_active(self) -> list[TagSkill]:
        pass