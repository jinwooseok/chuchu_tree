from urllib.parse import urlencode

from app.common.domain.service.oauth_client import OAuthClient
from app.common.domain.vo.oauth_token import OAuthToken
from app.common.domain.vo.oauth_user_info import GitHubUserInfo


class GitHubOAuthClient(OAuthClient):
    """깃허브 OAuth 클라이언트"""

    TOKEN_URL = "https://github.com/login/oauth/access_token"
    USER_INFO_URL = "https://api.github.com/user"

    async def get_social_login_url(self, frontend_redirect_url: str | None, action: str = "login") -> str:

        encoded_state = await self.encode_redirect_url_to_state(frontend_redirect_url, action)

        params = {
            "client_id": self.settings.GITHUB_CLIENT_ID,
            "redirect_uri": self.settings.GITHUB_REDIRECT_URI,
            "scope": "read:user user:email",
            "state": encoded_state,
        }

        return f"https://github.com/login/oauth/authorize?{urlencode(params)}"

    async def get_access_token(self, code: str, state: str = "") -> OAuthToken:
        """깃허브 액세스 토큰 획득"""
        data = {
            "client_id": self.settings.GITHUB_CLIENT_ID,
            "client_secret": self.settings.GITHUB_CLIENT_SECRET,
            "code": code,
            "redirect_uri": self.settings.GITHUB_REDIRECT_URI,
        }

        # GitHub requires Accept header for JSON response
        headers = {"Accept": "application/json"}

        response = await self.client.post(self.TOKEN_URL, data=data, headers=headers)
        response.raise_for_status()
        token_data = response.json()

        return OAuthToken(
            access_token=token_data["access_token"],
            token_type=token_data.get("token_type", "Bearer"),
            refresh_token=token_data.get("refresh_token"),
            expires_in=token_data.get("expires_in"),
            scope=token_data.get("scope")
        )

    async def get_user_info(self, access_token: str) -> GitHubUserInfo:
        """깃허브 사용자 정보 조회"""
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json"
        }
        response = await self.client.get(self.USER_INFO_URL, headers=headers)
        response.raise_for_status()
        user_data = response.json()

        return GitHubUserInfo.from_api_response(user_data)

    async def unlink(self, access_token: str) -> bool:
        """
        깃허브 연동 해제

        API: DELETE https://api.github.com/applications/{CLIENT_ID}/grant
        Headers: Basic Auth (CLIENT_ID, CLIENT_SECRET)
        Body: {"access_token": "..."}
        성공 시: 204 No Content
        """
        import base64

        url = f"https://api.github.com/applications/{self.settings.GITHUB_CLIENT_ID}/grant"

        # Basic Auth 인증 헤더 생성
        credentials = f"{self.settings.GITHUB_CLIENT_ID}:{self.settings.GITHUB_CLIENT_SECRET}"
        basic_auth = base64.b64encode(credentials.encode()).decode()

        headers = {
            "Authorization": f"Basic {basic_auth}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

        body = {"access_token": access_token}

        response = await self.client.delete(url, headers=headers, json=body)
        response.raise_for_status()

        return response.status_code == 204
