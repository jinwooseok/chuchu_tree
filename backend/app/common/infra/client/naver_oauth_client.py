import os
from typing import Any
from urllib.parse import urlencode
from app.common.domain.service.oauth_client import OAuthClient

class NaverOAuthClient(OAuthClient):
    """네이버 OAuth 클라이언트"""
    
    TOKEN_URL = "https://nid.naver.com/oauth2.0/token"
    USER_INFO_URL = "https://openapi.naver.com/v1/nid/me"
    
    def get_social_login_url(self, frontend_redirect_url: str | None) -> str:
        
        encoded_state = self.encode_redirect_url_to_state(frontend_redirect_url)
        
        params = {
            "response_type": "code",
            "client_id": self.settings.NAVER_CLIENT_ID,
            "redirect_uri": self.settings.NAVER_REDIRECT_URI,
            "state": encoded_state,
        }
        
        return f"https://nid.naver.com/oauth2.0/authorize?{urlencode(params)}"

    async def get_access_token(self, code: str, state: str = "") -> dict[str, Any]:
        """네이버 액세스 토큰 획득"""
        data = {
            "grant_type": "authorization_code",
            "client_id": self.settings.NAVER_CLIENT_ID,
            "client_secret": self.settings.NAVER_CLIENT_SECRET,
            "code": code,
            "state": state
        }
        
        response = await self.client.post(self.TOKEN_URL, data=data)
        response.raise_for_status()
        return response.json()
    
    async def get_user_info(self, access_token: str) -> dict[str, Any]:
        """네이버 사용자 정보 조회"""
        headers = {"Authorization": f"Bearer {access_token}"}
        response = await self.client.get(self.USER_INFO_URL, headers=headers)
        response.raise_for_status()
        return response.json()
    
    async def unlink(self, access_token: str) -> dict[str, Any]:
        """네이버 토큰 삭제 (연동해제)"""
        data = {
            "grant_type": "delete",
            "client_id": self.settings.NAVER_CLIENT_ID,
            "client_secret": self.settings.NAVER_CLIENT_SECRET,
            "access_token": access_token
        }
        
        response = await self.client.post(self.TOKEN_URL, data=data)
        response.raise_for_status()
        return response.json()