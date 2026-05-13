import pytest
from httpx import AsyncClient


class TestGetAllTags:
    """GET /api/v1/tags - 전체 태그 목록 (인증 불필요)"""

    async def test_get_all_tags_returns_200(self, integration_client: AsyncClient):
        resp = await integration_client.get("/api/v1/tags")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == 200
        assert "tags" in data["data"]

    async def test_get_all_tags_returns_list(self, integration_client: AsyncClient):
        resp = await integration_client.get("/api/v1/tags")
        data = resp.json()
        assert isinstance(data["data"]["tags"], list)
