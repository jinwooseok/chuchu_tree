import httpx
from app.config.settings import get_settings

class OAuthClient:
    def __init__(self):
        self.client = httpx.AsyncClient()
        self.settings = get_settings()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
