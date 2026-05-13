import pytest
from httpx import AsyncClient


class TestProblemSearch:
    """GET /api/v1/problems/search - 문제 검색"""

    async def test_search_returns_200(self, integration_client: AsyncClient):
        resp = await integration_client.get("/api/v1/problems/search", params={"keyword": "1000"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == 200

    async def test_search_no_results(self, integration_client: AsyncClient):
        resp = await integration_client.get(
            "/api/v1/problems/search",
            params={"keyword": "zzzznonexistent99999"},
        )
        assert resp.status_code == 200

    async def test_search_without_keyword_fails(self, integration_client: AsyncClient):
        resp = await integration_client.get("/api/v1/problems/search")
        assert resp.status_code == 400  # validation error
