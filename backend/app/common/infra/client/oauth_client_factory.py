from abc import ABC, abstractmethod

from app.common.domain.service.oauth_client import OAuthClient
from app.common.infra.client.kakao_oauth_client import KakaoOAuthClient
from app.common.infra.client.naver_oauth_client import NaverOAuthClient

class OAuthClientFactory(ABC):
    """OAuth 클라이언트 팩토리 기본 클래스"""
    
    @abstractmethod
    def create_client(self) -> OAuthClient:
        pass

class KakaoClientFactory(OAuthClientFactory):
    """카카오 클라이언트 팩토리"""
    
    def create_client(self):
        return KakaoOAuthClient()

class NaverClientFactory(OAuthClientFactory):
    """네이버 클라이언트 팩토리"""
    
    def create_client(self):
        return NaverOAuthClient()