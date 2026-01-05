# """Google Ads API Client"""
# from typing import Any
# from datetime import datetime
# import httpx
# import logging

# from app.common.domain.service.oauth_client import OAuthClient
# from app.common.domain.vo.oauth_token import OAuthToken

# logger = logging.getLogger(__name__)


# class GoogleOAuthClient(OAuthClient):
#     """
#     Google OAUTH 클라이언트
#     """

#     # OAuth Endpoints
#     TOKEN_URL = "https://oauth2.googleapis.com/token"
#     REVOKE_URL = "https://oauth2.googleapis.com/revoke"

#     async def get_social_login_url(self, frontend_redirect_url: str | None) -> str:

#         encoded_state = await self.encode_redirect_url_to_state(frontend_redirect_url)

#         params = {
#             "client_id": self.settings.KAKAO_CLIENT_ID,
#             "redirect_uri": self.settings.KAKAO_REDIRECT_URI,
#             "response_type": "code",
#             "scope": "profile_nickname",
#             "state": encoded_state,
#         }

#         return f"https://kauth.kakao.com/oauth/authorize?{urlencode(params)}"
    
#     async def get_access_token(self, code: str, state: str = "") -> OAuthToken:
#         """카카오 액세스 토큰 획득"""
#         data = {
#             "grant_type": "authorization_code",
#             "client_id": self.settings.KAKAO_CLIENT_ID,
#             "client_secret": self.settings.KAKAO_CLIENT_SECRET,
#             "redirect_uri": self.settings.KAKAO_REDIRECT_URI,
#             "code": code
#         }
#         response = await self.client.post(self.TOKEN_URL, data=data)
#         response.raise_for_status()
#         token_data = response.json()

#         return OAuthToken(
#             access_token=token_data["access_token"],
#             token_type=token_data.get("token_type", "Bearer"),
#             refresh_token=token_data.get("refresh_token"),
#             expires_in=token_data.get("expires_in"),
#             scope=token_data.get("scope")
#         )

#     async def get_user_info(self, access_token: str) -> GoogleUserInfo:
#         """카카오 사용자 정보 조회"""
#         headers = {"Authorization": f"Bearer {access_token}"}
#         response = await self.client.get(self.USER_INFO_URL, headers=headers)
#         response.raise_for_status()
#         user_data = response.json()

#         return GoogleUserInfo.from_api_response(user_data)

#     async def unlink(self, access_token: str) -> bool:
#         """카카오 연동 해제"""
#         headers = {"Authorization": f"Bearer {access_token}"}
#         response = await self.client.post(self.UNLINK_URL, headers=headers)
#         response.raise_for_status()
#         return True