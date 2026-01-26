from fastapi import Response
from urllib.parse import urlparse
from typing import Optional
from app.common.domain.service.cookie_service import CookieService


class FastAPICookieService(CookieService):
    """FastAPI 구현체"""

    def __init__(self, environment: str):
        self.environment = environment

    def set_cookie(self, response:Response, name: str, value: str, max_age: int, **kwargs):
        if self.environment == "prod":
            response.set_cookie(
            key=name,
            value=value,
            max_age=max_age,
            httponly=kwargs.get('httponly', True),
            secure=kwargs.get('secure', True),
            samesite=kwargs.get('samesite', 'lax')
        )
        elif self.environment == "dev":

            response.set_cookie(
                key=name,
                value=value,
                max_age=max_age,
                httponly=kwargs.get('httponly', True),
                secure=kwargs.get('secure', False),
                samesite=kwargs.get('samesite', 'lax'),
            )
        else:
            response.set_cookie(
                key=name,
                value=value,
                max_age=max_age,
                httponly=kwargs.get('httponly', True),
                secure=kwargs.get('secure', False),
                samesite=kwargs.get('samesite', 'lax')
            )
    
    def delete_cookie(self, response:Response, name: str, **kwargs):
        response.delete_cookie(name)
        response.delete_cookie(name)