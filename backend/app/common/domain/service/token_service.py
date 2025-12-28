from abc import abstractmethod
from datetime import timedelta
class TokenService:
    @abstractmethod
    def create_token(self, payload: dict, expires_delta: timedelta) -> str:
        pass
    
    @abstractmethod  
    def decode_token(self, token: str) -> dict:
        pass