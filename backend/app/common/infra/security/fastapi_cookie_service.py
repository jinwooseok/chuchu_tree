from fastapi import Response
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
                samesite=kwargs.get('samesite', 'lax')
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
        # 쿠키 삭제 시 설정할 때와 동일한 속성 사용
        # 쿠키를 완전히 삭제하기 위해 만료된 값으로 덮어씀
        response.set_cookie(
            key=name,
            value="",  # 빈 값
            max_age=0,  # 즉시 만료
            expires=0,  # 즉시 만료
            httponly=kwargs.get('httponly', True),
            secure=kwargs.get('secure', False),
            samesite=kwargs.get('samesite', 'none'),
            domain=kwargs.get('domain', None),
            path=kwargs.get('path', "/")
        )