from abc import ABC, abstractmethod

from app.common.domain.vo.identifiers import UserAccountId
from app.user.domain.entity.user_account import UserAccount
from app.user.domain.enums import Provider

class UserAccountRepository(ABC):
    """Repository 인터페이스"""
    
    @abstractmethod
    async def save(self, user_account: UserAccount) -> UserAccount:
        """유저 저장"""
        pass
    
    @abstractmethod
    async def find_by_id(self, user_id: UserAccountId) -> UserAccount|None:
        """ID로 유저 조회"""
        pass
    
    @abstractmethod
    async def find_by_provider(
        self, 
        provider: Provider, 
        provider_id: str
    ) -> UserAccount|None:
        """Provider 정보로 유저 조회"""
        pass
    
    @abstractmethod
    async def exists_by_id(self, user_id: UserAccountId) -> bool:
        """유저 존재 여부 확인"""
        pass