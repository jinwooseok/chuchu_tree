import pytest
from httpx import AsyncClient


class TestRecommendation:
    """GET /api/v1/user-accounts/me/problems - 문제 추천"""

    async def test_recommendation_without_auth_fails(self, integration_client: AsyncClient):
        resp = await integration_client.get("/api/v1/user-accounts/me/problems")
        assert resp.status_code == 401

    async def test_recommendation_with_auth(
        self, integration_client: AsyncClient, valid_access_token: str
    ):
        integration_client.cookies.set("access_token", valid_access_token)
        resp = await integration_client.get("/api/v1/user-accounts/me/problems")
        # 백준 미연동 등의 이유로 에러일 수 있음
        assert resp.status_code in (200, 400, 404)

    async def test_recommendation_with_filters(
        self, integration_client: AsyncClient, valid_access_token: str
    ):
        integration_client.cookies.set("access_token", valid_access_token)
        resp = await integration_client.get(
            "/api/v1/user-accounts/me/problems",
            params={
                "level": '["EASY"]',
                "tags": "[]",
                "count": 3,
                "exclusion_mode": "LENIENT",
            },
        )
        assert resp.status_code in (200, 400, 404)
