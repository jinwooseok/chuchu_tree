import pytest
from unittest.mock import AsyncMock

from app.common.infra.gateway.refresh_token_whitelist_gateway_impl import RefreshTokenWhitelistGatewayImpl


class TestRefreshTokenWhitelistGateway:
    """RefreshTokenWhitelistGatewayImpl 단위 테스트"""

    def _make_gateway(self) -> tuple[RefreshTokenWhitelistGatewayImpl, AsyncMock]:
        redis_client = AsyncMock()
        gateway = RefreshTokenWhitelistGatewayImpl(redis_client=redis_client)
        return gateway, redis_client

    async def test_store_token(self):
        gateway, redis = self._make_gateway()
        redis.set.return_value = True

        result = await gateway.store_token(user_id=42, jti="test-jti", ttl_seconds=604800)

        assert result is True
        redis.set.assert_called_once()
        call_args = redis.set.call_args
        assert call_args[0][0] == "rt:42:test-jti"
        assert call_args[0][1] == "valid"

    async def test_is_token_valid_exists(self):
        gateway, redis = self._make_gateway()
        redis.exists.return_value = True

        result = await gateway.is_token_valid(user_id=42, jti="test-jti")

        assert result is True
        redis.exists.assert_called_once_with("rt:42:test-jti")

    async def test_is_token_valid_not_exists(self):
        gateway, redis = self._make_gateway()
        redis.exists.return_value = False

        result = await gateway.is_token_valid(user_id=42, jti="unknown-jti")

        assert result is False

    async def test_revoke_token(self):
        gateway, redis = self._make_gateway()
        redis.delete.return_value = 1

        result = await gateway.revoke_token(user_id=42, jti="test-jti")

        assert result is True
        redis.delete.assert_called_once_with("rt:42:test-jti")

    async def test_revoke_token_not_found(self):
        gateway, redis = self._make_gateway()
        redis.delete.return_value = 0

        result = await gateway.revoke_token(user_id=42, jti="missing-jti")

        assert result is False

    async def test_mark_as_used(self):
        gateway, redis = self._make_gateway()
        redis.set.return_value = True

        result = await gateway.mark_as_used(jti="test-jti", user_id=42, ttl_seconds=604800)

        assert result is True
        call_args = redis.set.call_args
        assert call_args[0][0] == "rt:used:test-jti"
        assert call_args[0][1] == "42"

    async def test_is_token_used_returns_user_id(self):
        gateway, redis = self._make_gateway()
        redis.get.return_value = 42  # user_id

        result = await gateway.is_token_used(jti="used-jti")

        assert result == 42
        redis.get.assert_called_once_with("rt:used:used-jti")

    async def test_is_token_used_returns_none_when_not_used(self):
        gateway, redis = self._make_gateway()
        redis.get.return_value = None

        result = await gateway.is_token_used(jti="fresh-jti")

        assert result is None

    async def test_revoke_all_user_tokens(self):
        gateway, redis = self._make_gateway()
        redis.keys.return_value = ["rt:42:jti1", "rt:42:jti2", "rt:42:jti3"]
        redis.delete.return_value = 3

        result = await gateway.revoke_all_user_tokens(user_id=42)

        assert result == 3
        redis.keys.assert_called_once_with("rt:42:*")
        redis.delete.assert_called_once_with("rt:42:jti1", "rt:42:jti2", "rt:42:jti3")

    async def test_revoke_all_user_tokens_no_keys(self):
        gateway, redis = self._make_gateway()
        redis.keys.return_value = []

        result = await gateway.revoke_all_user_tokens(user_id=42)

        assert result == 0
        redis.delete.assert_not_called()

    async def test_store_token_redis_error_returns_false(self):
        gateway, redis = self._make_gateway()
        redis.set.side_effect = Exception("Redis connection error")

        result = await gateway.store_token(user_id=42, jti="test-jti", ttl_seconds=604800)

        assert result is False

    async def test_is_token_valid_redis_error_returns_false(self):
        gateway, redis = self._make_gateway()
        redis.exists.side_effect = Exception("Redis connection error")

        result = await gateway.is_token_valid(user_id=42, jti="test-jti")

        assert result is False
