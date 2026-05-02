import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


class TestAuthMe:
    """GET /api/v1/auth/me 테스트"""

    async def test_auth_me_success_with_valid_token(
        self, integration_client: AsyncClient, valid_access_token: str
    ):
        """유효한 토큰으로 인증 확인 - 성공"""
        integration_client.cookies.set("access_token", valid_access_token)
        response = await integration_client.get("/api/v1/auth/me")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == 200
        assert data["message"] == "ok"

    async def test_auth_me_fails_without_token(self, integration_client: AsyncClient):
        """토큰 없이 호출 - NO_LOGIN_STATUS 에러"""
        response = await integration_client.get("/api/v1/auth/me")

        assert response.status_code == 401
        data = response.json()
        assert data["error"]["code"] == "NO_LOGIN_STATUS"

    async def test_auth_me_fails_with_expired_token(
        self, integration_client: AsyncClient, expired_access_token: str
    ):
        """만료된 토큰 - EXPIRED_TOKEN 에러"""
        integration_client.cookies.set("access_token", expired_access_token)
        response = await integration_client.get("/api/v1/auth/me")

        assert response.status_code == 401
        data = response.json()
        assert data["error"]["code"] == "EXPIRED_TOKEN"

    async def test_auth_me_fails_with_invalid_token(
        self, integration_client: AsyncClient, invalid_access_token: str
    ):
        """유효하지 않은 토큰 - INVALID_TOKEN 에러"""
        integration_client.cookies.set("access_token", invalid_access_token)
        response = await integration_client.get("/api/v1/auth/me")

        assert response.status_code == 401
        data = response.json()
        assert data["error"]["code"] == "INVALID_TOKEN"
