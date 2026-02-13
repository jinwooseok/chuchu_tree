import pytest
from httpx import AsyncClient


class TestSocialLogin:
    """GET /api/v1/auth/login/{provider} - 소셜 로그인 URL 리다이렉트"""

    async def test_kakao_login_redirects(self, integration_client: AsyncClient):
        resp = await integration_client.get("/api/v1/auth/login/kakao", follow_redirects=False)
        assert resp.status_code == 302
        assert "kakao" in resp.headers.get("location", "").lower()

    async def test_naver_login_redirects(self, integration_client: AsyncClient):
        resp = await integration_client.get("/api/v1/auth/login/naver", follow_redirects=False)
        assert resp.status_code == 302
        assert "naver" in resp.headers.get("location", "").lower()

    async def test_google_login_redirects(self, integration_client: AsyncClient):
        resp = await integration_client.get("/api/v1/auth/login/google", follow_redirects=False)
        assert resp.status_code == 302
        assert "google" in resp.headers.get("location", "").lower()

    async def test_github_login_redirects(self, integration_client: AsyncClient):
        resp = await integration_client.get("/api/v1/auth/login/github", follow_redirects=False)
        assert resp.status_code == 302
        assert "github" in resp.headers.get("location", "").lower()


class TestLogout:
    """POST /api/v1/auth/logout"""

    async def test_logout_clears_cookies(
        self, integration_client: AsyncClient, valid_access_token: str
    ):
        integration_client.cookies.set("access_token", valid_access_token)
        resp = await integration_client.post("/api/v1/auth/logout")
        assert resp.status_code == 200

        # 쿠키 삭제 확인 (Set-Cookie 헤더에 max-age=0 등)
        set_cookies = resp.headers.get_list("set-cookie")
        cookie_names = [c.split("=")[0].strip() for c in set_cookies]
        assert "access_token" in cookie_names
        assert "refresh_token" in cookie_names

    async def test_logout_without_token_fails(self, integration_client: AsyncClient):
        resp = await integration_client.post("/api/v1/auth/logout")
        assert resp.status_code == 401


class TestRefreshToken:
    """POST /api/v1/auth/token/refresh"""

    async def test_refresh_without_token_fails(self, integration_client: AsyncClient):
        resp = await integration_client.post("/api/v1/auth/token/refresh")
        assert resp.status_code == 401
        data = resp.json()
        assert data["error"]["code"] == "INVALID_TOKEN"


class TestWithdraw:
    """GET /api/v1/auth/withdraw"""

    async def test_withdraw_without_token_fails(self, integration_client: AsyncClient):
        resp = await integration_client.get("/api/v1/auth/withdraw")
        assert resp.status_code == 401
