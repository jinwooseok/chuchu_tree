from abc import ABC, abstractmethod

from app.common.domain.enums import SkillCode, TagLevel
from app.common.domain.vo.identifiers import TagSkillId, TagId
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
    async def find_by_tag_id_and_code(
        self,
        tag_id: TagId,
        code: SkillCode
    ) -> TagSkill | None:
        """태그별 스킬 조회 (per-tag lookup)"""
        pass

    @abstractmethod
    async def find_all_by_tag_id(self, tag_id: TagId) -> list[TagSkill]:
        """특정 태그의 모든 스킬 조회"""
        pass

    @abstractmethod
    async def find_all_active(self) -> list[TagSkill]:
        pass