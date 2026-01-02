from pydantic import BaseModel, Field, field_validator

from app.common.domain.enums import Provider
from app.core.error_codes import ErrorCode
from app.core.exception import APIException


class SocialLoginCommand(BaseModel):
    provider: str = Field(..., description="소셜로그인 제공자 (google, kakao, naver)")
    frontend_redirect_url: str | None = Field(None, description="로그인 후 리다이렉트될 프론트엔드 URL")
    
    @field_validator('provider', mode="before")
    @classmethod
    def validate_provider(cls, v: str):
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Provider validation - Input: '{v}', Type: {type(v)}, Upper: '{v.upper()}'")
        logger.info(f"Valid providers: {list(Provider._value2member_map_.keys())}")

        if not Provider.has_value(v.upper()):
            logger.error(f"Provider validation failed for: '{v.upper()}'")
            raise APIException(ErrorCode.INVALID_PROVIDER)
        return v.upper()