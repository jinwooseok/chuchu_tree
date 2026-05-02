from dataclasses import dataclass


@dataclass(frozen=True)
class OAuthToken:
    """OAuth 액세스 토큰 Value Object"""

    access_token: str
    refresh_token: str | None
    expires_in: int | None
    scope: str | None = None
    token_type: str = "Bearer"

    @property
    def is_expired(self) -> bool:
        """토큰 만료 여부 확인 (만료 시간이 있을 경우)"""
        if self.expires_in is None:
            return False
        if self.expires_in > 0:
            return False
        return True

    class Config:
        frozen = True 
