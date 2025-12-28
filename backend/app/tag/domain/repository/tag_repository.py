from abc import ABC, abstractmethod

from app.common.domain.vo.identifiers import TagId
from app.tag.domain.entity.tag import Tag
from app.tag.domain.enums import TagLevel

class TagRepository(ABC):
    """Repository 인터페이스"""
    
    @abstractmethod
    async def save(self, tag: Tag) -> Tag:
        pass
    
    @abstractmethod
    async def find_by_id(self, tag_id: TagId) -> Tag|None:
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