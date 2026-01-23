from abc import ABC, abstractmethod

from app.common.domain.enums import Provider
from app.common.domain.vo.identifiers import UserAccountId
from app.user.domain.entity.user_account import UserAccount

class UserAccountRepository(ABC):
    """Repository 인터페이스"""
    
    @abstractmethod
    async def insert(self, user_account: UserAccount) -> UserAccount:
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

    @abstractmethod
    async def update(self, user_account: UserAccount) -> UserAccount:
        """유저 업데이트"""
        pass

    @abstractmethod
    async def delete(self, user_account: UserAccount) -> None:
        """
        사용자 계정 삭제 (Hard Delete)
        연관 데이터(targets, account_links)도 함께 삭제
        """
        pass