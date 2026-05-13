from abc import ABC, abstractmethod

from app.common.domain.enums import TagLevel
from app.common.domain.vo.identifiers import TagId
from app.tag.domain.entity.tag import Tag

class TagRepository(ABC):
    """Repository 인터페이스"""

    @abstractmethod
    async def save(self, tag: Tag) -> Tag:
        pass

    @abstractmethod
    async def find_by_id(self, tag_id: TagId) -> Tag|None:
        pass

    @abstractmethod
    async def find_by_ids(self, tag_ids: list[TagId]) -> list[Tag]:
        """여러 ID로 조회"""
        pass
        
    @abstractmethod
    async def find_by_ids_and_active(self, tag_ids: list[TagId]) -> list[Tag]:
        """여러 ID로 조회"""
        pass    
    
    @abstractmethod
    async def find_by_code(self, code: str) -> Tag|None:
        pass

    @abstractmethod
    async def find_by_level(self, level: TagLevel) -> list[Tag]:
        pass

    @abstractmethod
    async def find_active_tags(self) -> list[Tag]:
        pass

    @abstractmethod
    async def find_active_tags_with_relations(self) -> list[Tag]:
        """
        활성 태그를 선수 태그 관계 및 연관 목표와 함께 조회

        Eager loading:
        - parent_tag_relations (선수 태그)
        - targets (연관 목표)

        Returns:
            Tag 리스트 (parent_tag_relations, targets 포함)
        """
        pass
