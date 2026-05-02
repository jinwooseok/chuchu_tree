import uuid
from datetime import datetime, timedelta, timezone

from jose import ExpiredSignatureError, JWTError, jwt

from app.common.domain.service.token_service import TokenService
from app.config.settings import get_settings
from app.core.error_codes import ErrorCode
from app.core.exception import APIException


class JwtTokenService(TokenService):
    """JWT를 사용한 토큰 서비스 구현체"""

    def __init__(self, secret_key, algorithm):
        self.secret_key = secret_key
        self.algorithm = algorithm

    def create_token(self, payload: dict, expires_delta: timedelta) -> str:
        expire = datetime.now(timezone.utc) + expires_delta
        payload.update({"exp": expire})
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def create_refresh_token(self, payload: dict, expires_delta: timedelta) -> tuple[str, str]:
        jti = str(uuid.uuid4())
        expire = datetime.now(timezone.utc) + expires_delta
        payload.update({"exp": expire, "jti": jti, "type": "refresh"})
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return token, jti

    def decode_token(self, token: str) -> dict:
        try:
            return jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
        except ExpiredSignatureError:
            raise APIException(ErrorCode.EXPIRED_TOKEN)
        except JWTError:
            raise APIException(ErrorCode.INVALID_TOKEN)