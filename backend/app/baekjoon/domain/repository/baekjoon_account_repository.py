from abc import ABC, abstractmethod

from app.baekjoon.domain.entity.baekjoon_account import BaekjoonAccount
from app.common.domain.vo.identifiers import BaekjoonAccountId, UserAccountId

class BaekjoonAccountRepository(ABC):
    """Repository 인터페이스"""
    
    @abstractmethod
    async def save(self, account: BaekjoonAccount) -> BaekjoonAccount:
        pass
    
    @abstractmethod
    async def find_by_id(self, account_id: BaekjoonAccountId) -> BaekjoonAccount|None:
        pass
    
    @abstractmethod
    async def find_by_user_id(self, user_id: UserAccountId) -> BaekjoonAccount|None:
        pass