import logging
from datetime import timedelta

from app.common.domain.gateway.csrf_token_gateway import CsrfTokenGateway
from app.common.infra.client.redis_client import AsyncRedisClient

logger = logging.getLogger(__name__)


class CsrfTokenGatewayImpl(CsrfTokenGateway):
    """Redis를 사용한 CSRF 토큰 Gateway 구현"""

    def __init__(self, redis_client: AsyncRedisClient):
        self.redis_client = redis_client

    async def store_token(self, token: str, ttl_minutes: int = 10) -> bool:
        """CSRF 토큰을 Redis에 저장"""
        try:
            redis_key = f"oauth:csrf:{token}"
            result = await self.redis_client.set(
                redis_key,
                "valid",
                ex=timedelta(minutes=ttl_minutes)
            )
            return result
        except Exception as e:
            logger.error(f"CSRF 토큰 저장 실패: {e}")
            return False

    async def verify_and_delete_token(self, token: str) -> bool:
        """CSRF 토큰 검증 및 삭제 (일회용)"""
        try:
            redis_key = f"oauth:csrf:{token}"

            # 토큰 존재 확인
            exists = await self.redis_client.exists(redis_key)

            if exists:
                # 검증 후 즉시 삭제 (일회용)
                await self.redis_client.delete(redis_key)
                return True
            else:
                logger.warning(f"CSRF 토큰 검증 실패 (존재하지 않음)")
                return False

        except Exception as e:
            logger.error(f"CSRF 토큰 검증 중 에러: {e}")
            return False
