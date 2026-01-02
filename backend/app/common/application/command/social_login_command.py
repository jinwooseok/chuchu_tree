from pydantic import BaseModel, Field, field_validator

from app.common.domain.enums import Provider
from app.core.error_codes import ErrorCode
from app.core.exception import APIException


class SocialLoginCommand(BaseModel):
    provider: Provider = Field(..., description="소셜로그인 제공자 (google, kakao, naver)")
    frontend_redirect_url: str | None = Field(None, description="로그인 후 리다이렉트될 프론트엔드 URL")
    
    @field_validator('provider')
    @classmethod
    def validate_provider(cls, v: str):
        if not Provider.has_value(v.upper()):
            raise APIException(ErrorCode.INVALID_PROVIDER)
        return Provider(v)