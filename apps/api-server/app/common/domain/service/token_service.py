from abc import abstractmethod
from datetime import timedelta


class TokenService:
    @abstractmethod
    def create_token(self, payload: dict, expires_delta: timedelta) -> str:
        pass

    @abstractmethod
    def create_refresh_token(self, payload: dict, expires_delta: timedelta) -> tuple[str, str]:
        """Refresh Token 생성 (jti 포함)

        Returns:
            tuple[str, str]: (token_string, jti)
        """
        pass

    @abstractmethod
    def decode_token(self, token: str) -> dict:
        pass