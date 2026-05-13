from abc import ABC, abstractmethod

from app.common.domain.vo.identifiers import TargetId
from app.target.domain.entity.target import Target

class TargetRepository(ABC):
    """Repository 인터페이스"""
    
    @abstractmethod
    async def save(self, target: Target) -> Target:
        """목표 저장"""
        pass
    
    @abstractmethod
    async def find_by_id(self, target_id: TargetId) -> Target | None:
        """ID로 목표 조회"""
        pass
    
    @abstractmethod
    async def find_by_code(self, code: str) -> Target | None:
        """코드로 목표 조회"""
        pass
    
    @abstractmethod
    async def find_all_active(self) -> list[Target]:
        """모든 활성화된 목표 조회"""
        pass
    
    @abstractmethod
    async def exists_by_code(self, code: str) -> bool:
        """코드 존재 여부 확인"""
        pass
    
    @abstractmethod
    async def find_by_ids(self, target_ids: list[TargetId]) -> list[Target]:
        """여러 ID로 목표 조회"""
        pass