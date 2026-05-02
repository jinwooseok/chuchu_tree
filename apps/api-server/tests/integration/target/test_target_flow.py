import pytest
from httpx import AsyncClient


class TestGetAllTargets:
    """GET /api/v1/targets - 전체 목표 목록 (인증 불필요)"""

    async def test_get_all_targets_returns_200(self, integration_client: AsyncClient):
        resp = await integration_client.get("/api/v1/targets")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == 200

    async def test_get_all_targets_returns_list(self, integration_client: AsyncClient):
        resp = await integration_client.get("/api/v1/targets")
        data = resp.json()
        assert isinstance(data["data"]["targets"], list)

    async def test_target_items_have_required_fields(self, integration_client: AsyncClient):
        resp = await integration_client.get("/api/v1/targets")
        data = resp.json()
        targets = data["data"]["targets"]
        if targets:
            first = targets[0]
            assert "targetId" in first
            assert "targetCode" in first
            assert "targetDisplayName" in first
