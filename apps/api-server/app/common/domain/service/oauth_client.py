from abc import ABC, abstractmethod
import os
import secrets
import httpx

from app.common.domain.gateway.csrf_token_gateway import CsrfTokenGateway
from app.common.domain.vo.oauth_token import OAuthToken
from app.common.domain.vo.oauth_user_info import OAuthUserInfo
from app.config.settings import get_settings


class OAuthClient(ABC):
    def __init__(self, csrf_gateway: 'CsrfTokenGateway | None' = None):
        self.client = httpx.AsyncClient()
        self.settings = get_settings()
        self.csrf_gateway = csrf_gateway
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    @abstractmethod
    async def get_social_login_url(self, frontend_redirect_url: str | None, action: str = "login") -> str:
        pass
    
    @abstractmethod
    async def get_access_token(self, code: str, state: str = "") -> OAuthToken:
        """OAuth 액세스 토큰 획득"""
        pass

    @abstractmethod
    async def get_user_info(self, access_token: str) -> OAuthUserInfo:
        """OAuth 사용자 정보 조회"""
        pass

    @abstractmethod
    async def unlink(self, access_token: str) -> bool:
        """OAuth 연동 해제"""
        pass
    
    async def encode_redirect_url_to_state(self, url: str, action: str = "login"):
        """
        CSRF 토큰과 redirect URL, action을 state에 인코딩
        CSRF 토큰은 Gateway를 통해 15분간 저장되어 콜백에서 검증됨

        Args:
            url: 프론트엔드 리다이렉트 URL
            action: "login" 또는 "withdraw" (기본값: "login")
        """
        import base64
        import json

        # CSRF 토큰 생성 (32바이트 URL-safe 랜덤 문자열)
        csrf_token = secrets.token_urlsafe(32)

        # Gateway를 통해 CSRF 토큰 저장 (15분 만료)
        if self.csrf_gateway:
            await self.csrf_gateway.store_token(csrf_token, ttl_minutes=15)

        # Redirect URL 결정
        redirect_url = url if (url and os.getenv("environment") != "prod") else self.settings.FRONTEND_REDIRECT_URI


        # State 데이터 구성
        state_data = {
            "csrf_token": csrf_token,
            "frontend_redirect_url": redirect_url,
            "action": action
        }

        # Base64 인코딩
        encoded_state = base64.b64encode(json.dumps(state_data).encode()).decode()
        return encoded_state

    async def verify_csrf_token(self, csrf_token: str) -> bool:
        """
        CSRF 토큰 검증 및 삭제 (일회용)
        Gateway를 통해 검증하고 즉시 삭제
        """
        return await self.csrf_gateway.verify_and_delete_token(csrf_token)
        
    