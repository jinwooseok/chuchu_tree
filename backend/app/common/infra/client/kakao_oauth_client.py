from typing import Any
from app.common.domain.service.oauth_client import OAuthClient


class KakaoOAuthClient(OAuthClient):
    TOKEN_URL = "https://kauth.kakao.com/oauth/token"
    USER_INFO_URL = "https://kapi.kakao.com/v2/user/me"
    UNLINK_URL = "https://kapi.kakao.com/v1/user/unlink"
    
    async def get_access_token(self, code: str) -> dict[str, Any]:
        data = {
            "grant_type": "authorization_code",
            "client_id": self.settings.KAKAO_CLIENT_ID,
            "client_secret": self.settings.KAKAO_CLIENT_SECRET,
            "redirect_uri": self.settings.KAKAO_REDIRECT_URI,
            "code": code
        }
        response = await self.client.post(self.TOKEN_URL, data=data)
        response.raise_for_status()
        return response.json()
    
    async def get_user_info(self, access_token: str) -> dict[str, Any]:
        headers = {"Authorization": f"Bearer {access_token}"}
        response = await self.client.get(self.USER_INFO_URL, headers=headers)
        response.raise_for_status()
        return response.json()
    
    async def unlink(self, access_token: str) -> dict[str, Any]:
        headers = {"Authorization": f"Bearer {access_token}"}
        response = await self.client.post(self.UNLINK_URL, headers=headers)
        response.raise_for_status()
        return response.json()