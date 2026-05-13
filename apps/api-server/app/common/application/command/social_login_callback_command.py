from pydantic import BaseModel, Field, field_validator, ConfigDict
from fastapi import Request, Response

from app.common.domain.enums import Provider
from app.core.error_codes import ErrorCode
from app.core.exception import APIException


class SocialLoginCallbackCommand(BaseModel):
    """소셜 로그인 콜백 Command"""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    provider: str = Field(..., description="소셜 로그인 제공자 (kakao, naver, google)")
    code: str = Field(..., description="OAuth 인가 코드")
    state: str = Field(..., description="CSRF 토큰 및 리다이렉트 URL이 포함된 state")
    request: Request = Field(..., description="FastAPI Request 객체")
    response: Response = Field(..., description="FastAPI Response 객체")

    @field_validator('provider', mode="before")
    @classmethod
    def validate_provider(cls, v: str) -> str:
        """Provider 검증 및 대문자 변환"""
        if not Provider.has_value(v.upper()):
            raise APIException(ErrorCode.INVALID_PROVIDER)
        return v.upper()

    @field_validator('state')
    @classmethod
    def validate_state(cls, v: str) -> str:
        """State 값 검증"""
        if not v or len(v.strip()) == 0:
            raise APIException(ErrorCode.INVALID_REQUEST)
        return v
