import pytest
from datetime import timedelta
from httpx import AsyncClient


class TestUserAccountAuth:
    """유저 계정 API - 인증 필요 엔드포인트"""

    async def test_profile_image_without_auth_fails(self, integration_client: AsyncClient):
        resp = await integration_client.post("/api/v1/user-accounts/profile-image")
        assert resp.status_code == 401

    async def test_delete_profile_image_without_auth_fails(self, integration_client: AsyncClient):
        resp = await integration_client.delete("/api/v1/user-accounts/profile-image")
        assert resp.status_code == 401

    async def test_get_user_tags_without_auth_fails(self, integration_client: AsyncClient):
        resp = await integration_client.get("/api/v1/user-accounts/me/tags")
        assert resp.status_code == 401

    async def test_get_user_targets_without_auth_fails(self, integration_client: AsyncClient):
        resp = await integration_client.get("/api/v1/user-accounts/me/targets")
        assert resp.status_code == 401

    async def test_update_user_target_without_auth_fails(self, integration_client: AsyncClient):
        resp = await integration_client.post(
            "/api/v1/user-accounts/me/targets",
            json={"targetCode": "COTE"},
        )
        assert resp.status_code == 401


class TestUserAccountAuthenticated:
    """유저 계정 API - 인증된 상태
        백준 계정 필요
    """

    async def test_get_user_tags(
        self, integration_client: AsyncClient,
        linked_baekjoon_account, baekjoon_test_user, token_service
    ):
        access_token = token_service.create_token(
            payload={"user_account_id": baekjoon_test_user.user_account_id},
            expires_delta=timedelta(hours=6)
        )
        integration_client.cookies.set("access_token", access_token)
        resp = await integration_client.get("/api/v1/user-accounts/me/tags")
        assert resp.status_code == 200

    async def test_get_user_targets(
        self, integration_client: AsyncClient, valid_access_token: str
    ):
        integration_client.cookies.set("access_token", valid_access_token)
        resp = await integration_client.get("/api/v1/user-accounts/me/targets")
        assert resp.status_code == 200

    async def test_delete_profile_image(
        self, integration_client: AsyncClient, valid_access_token: str
    ):
        integration_client.cookies.set("access_token", valid_access_token)
        resp = await integration_client.delete("/api/v1/user-accounts/profile-image")
        assert resp.status_code == 200


class TestAdminUserAccounts:
    """GET /api/v1/admin/user-accounts"""

    async def test_admin_without_auth_fails(self, integration_client: AsyncClient):
        resp = await integration_client.get("/api/v1/admin/user-accounts")
        assert resp.status_code == 401

    async def test_admin_with_auth(
        self, integration_client: AsyncClient, valid_access_token: str
    ):
        integration_client.cookies.set("access_token", valid_access_token)
        resp = await integration_client.get("/api/v1/admin/user-accounts")
        assert resp.status_code == 200
