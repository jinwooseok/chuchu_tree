from abc import ABC, abstractmethod
from typing import Optional


class RefreshTokenWhitelistGateway(ABC):
    """Refresh Token 화이트리스트 Gateway 인터페이스"""

    @abstractmethod
    async def store_token(self, user_id: int, jti: str, ttl_seconds: int) -> bool:
        """RT를 화이트리스트에 저장"""
        pass

    @abstractmethod
    async def is_token_valid(self, user_id: int, jti: str) -> bool:
        """RT가 화이트리스트에 존재하는지 확인"""
        pass

    @abstractmethod
    async def revoke_token(self, user_id: int, jti: str) -> bool:
        """특정 RT를 화이트리스트에서 삭제"""
        pass

    @abstractmethod
    async def mark_as_used(self, jti: str, user_id: int, ttl_seconds: int) -> bool:
        """사용된 RT로 기록 (재사용 감지용)"""
        pass

    @abstractmethod
    async def is_token_used(self, jti: str) -> Optional[int]:
        """RT가 이미 사용되었는지 확인. 사용됐으면 user_id 반환"""
        pass

    @abstractmethod
    async def revoke_all_user_tokens(self, user_id: int) -> int:
        """특정 유저의 모든 RT를 삭제"""
        pass
