import pytest
from httpx import AsyncClient


class TestBaekjoonAuth:
    """백준 API - 인증 필요 엔드포인트"""

    async def test_link_without_auth_fails(self, integration_client: AsyncClient):
        resp = await integration_client.post(
            "/api/v1/bj-accounts/link",
            json={"bjAccount": "test_bj"},
        )
        assert resp.status_code == 401

    async def test_get_me_without_auth_fails(self, integration_client: AsyncClient):
        resp = await integration_client.get("/api/v1/bj-accounts/me")
        assert resp.status_code == 401

    async def test_get_streak_without_auth_fails(self, integration_client: AsyncClient):
        resp = await integration_client.get(
            "/api/v1/bj-accounts/me/streak",
            params={"startDate": "2025-01-01", "endDate": "2025-01-31"},
        )
        assert resp.status_code == 401

    async def test_get_monthly_without_auth_fails(self, integration_client: AsyncClient):
        resp = await integration_client.get(
            "/api/v1/bj-accounts/me/problems",
            params={"year": 2025, "month": 1},
        )
        assert resp.status_code == 401

    async def test_get_unrecorded_without_auth_fails(self, integration_client: AsyncClient):
        resp = await integration_client.get("/api/v1/bj-accounts/unrecorded-problems/me")
        assert resp.status_code == 401

    async def test_refresh_without_auth_fails(self, integration_client: AsyncClient):
        resp = await integration_client.post("/api/v1/bj-accounts/me/refresh")
        assert resp.status_code == 401


class TestBaekjoonAuthenticated:
    """백준 API - 인증된 상태 (백준 연동 전이라 에러 예상)"""

    async def test_get_me_unlinked_user(
        self, integration_client: AsyncClient, valid_access_token: str
    ):
        """백준 미연동 유저 → UNLINKED_USER 에러"""
        integration_client.cookies.set("access_token", valid_access_token)
        resp = await integration_client.get("/api/v1/bj-accounts/me")
        # 연동 안 되어있으면 에러
        assert resp.status_code in (400, 404)

    async def test_get_streak_unlinked_user(
        self, integration_client: AsyncClient, valid_access_token: str
    ):
        integration_client.cookies.set("access_token", valid_access_token)
        resp = await integration_client.get(
            "/api/v1/bj-accounts/me/streak",
            params={"startDate": "2025-01-01", "endDate": "2025-01-31"},
        )
        assert resp.status_code in (400, 404)

    async def test_get_unrecorded_unlinked_user(
        self, integration_client: AsyncClient, valid_access_token: str
    ):
        integration_client.cookies.set("access_token", valid_access_token)
        resp = await integration_client.get("/api/v1/bj-accounts/unrecorded-problems/me")
        assert resp.status_code in (400, 404)
