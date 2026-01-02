from abc import ABC, abstractmethod
import os
import httpx
from app.config.dev_config import DevConfig
from app.config.local_config import LocalConfig
from app.config.prod_config import ProdConfig
from app.config.settings import get_settings

class OAuthClient(ABC):
    def __init__(self):
        self.client = httpx.AsyncClient()
        self.settings = get_settings()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    @abstractmethod
    def get_social_login_url(frontend_redirect_url: str | None) -> str:
        pass
    
    @abstractmethod
    async def get_access_token(self, code: str, state: str = "") -> dict[str, any]:
        pass
    
    @abstractmethod
    async def get_user_info(self, access_token: str) -> dict[str, any]:
        pass
    
    @abstractmethod
    async def unlink(self, access_token: str) -> dict[str, any]:
        pass
    
    def encode_redirect_url_to_state(self, url: str):
        import base64
        import json
        encoded_state = None
        if url and os.getenv("environment") != "prod":
            state_data = {"frontend_redirect_url": url}
            encoded_state = base64.b64encode(json.dumps(state_data).encode()).decode()
        else:
            state_data = {"frontend_redirect_url": self.settings.FRONTEND_REDIRECT_URI}
            encoded_state = base64.b64encode(json.dumps(state_data).encode()).decode()
        return encoded_state
        
    