import logging
from datetime import timedelta
from typing import Optional

from app.common.domain.gateway.refresh_token_whitelist_gateway import RefreshTokenWhitelistGateway
from app.common.infra.client.redis_client import AsyncRedisClient

logger = logging.getLogger(__name__)


class RefreshTokenWhitelistGatewayImpl(RefreshTokenWhitelistGateway):
    """Redis를 사용한 Refresh Token 화이트리스트 Gateway 구현"""

    def __init__(self, redis_client: AsyncRedisClient):
        self.redis_client = redis_client

    async def store_token(self, user_id: int, jti: str, ttl_seconds: int) -> bool:
        try:
            redis_key = f"rt:{user_id}:{jti}"
            return await self.redis_client.set(
                redis_key, "valid", ex=timedelta(seconds=ttl_seconds)
            )
        except Exception as e:
            logger.error(f"RT 저장 실패: {e}")
            return False

    async def is_token_valid(self, user_id: int, jti: str) -> bool:
        try:
            redis_key = f"rt:{user_id}:{jti}"
            return await self.redis_client.exists(redis_key)
        except Exception as e:
            logger.error(f"RT 검증 실패: {e}")
            return False

    async def revoke_token(self, user_id: int, jti: str) -> bool:
        try:
            redis_key = f"rt:{user_id}:{jti}"
            result = await self.redis_client.delete(redis_key)
            return result > 0
        except Exception as e:
            logger.error(f"RT 폐기 실패: {e}")
            return False

    async def mark_as_used(self, jti: str, user_id: int, ttl_seconds: int) -> bool:
        try:
            redis_key = f"rt:used:{jti}"
            return await self.redis_client.set(
                redis_key, str(user_id), ex=timedelta(seconds=ttl_seconds)
            )
        except Exception as e:
            logger.error(f"RT 사용 기록 실패: {e}")
            return False

    async def is_token_used(self, jti: str) -> Optional[int]:
        try:
            redis_key = f"rt:used:{jti}"
            value = await self.redis_client.get(redis_key)
            if value is not None:
                return int(value)
            return None
        except Exception as e:
            logger.error(f"RT 사용 여부 확인 실패: {e}")
            return None

    async def revoke_all_user_tokens(self, user_id: int) -> int:
        try:
            pattern = f"rt:{user_id}:*"
            keys = await self.redis_client.keys(pattern)
            if keys:
                return await self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"RT 일괄 삭제 실패: {e}")
            return 0
