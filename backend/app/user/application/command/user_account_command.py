"""User 모듈 Command 객체"""

from pydantic import BaseModel, Field, field_validator

from app.common.domain.enums import Provider
from app.core.error_codes import ErrorCode
from app.core.exception import APIException


class CreateUserAccountCommand(BaseModel):
    """
    사용자 계정 생성 명령
    """

    provider: str = Field(..., description="OAuth 제공자 (KAKAO, NAVER, GOOGLE)")
    provider_id: str = Field(..., description="제공자의 고유 사용자 ID")
    
    @field_validator('provider', mode="before")
    @classmethod
    def validate_provider(cls, v: str) -> str:
        """Provider 검증 및 대문자 변환"""
        if not Provider.has_value(v.upper()):
            raise APIException(ErrorCode.INVALID_PROVIDER)
        return v.upper()