from abc import ABC, abstractmethod

class CookieService(ABC):
    """쿠키 관리 추상화"""
    
    @abstractmethod
    def set_cookie(self, response, name: str, value: str, max_age: int, **kwargs):
        pass
    
    @abstractmethod
    def delete_cookie(self, response, name: str, **kwargs):
        pass