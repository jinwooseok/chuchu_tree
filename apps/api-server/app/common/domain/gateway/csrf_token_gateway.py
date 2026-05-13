from abc import ABC, abstractmethod


class CsrfTokenGateway(ABC):
    """CSRF 토큰 저장/검증을 위한 Gateway 인터페이스"""

    @abstractmethod
    async def store_token(self, token: str, ttl_minutes: int = 15) -> bool:
        """
        CSRF 토큰 저장

        Args:
            token: CSRF 토큰
            ttl_minutes: 만료 시간 (분)

        Returns:
            저장 성공 여부
        """
        pass

    @abstractmethod
    async def verify_and_delete_token(self, token: str) -> bool:
        """
        CSRF 토큰 검증 및 삭제 (일회용)

        Args:
            token: 검증할 CSRF 토큰

        Returns:
            토큰이 유효하면 True, 아니면 False
        """
        pass
