"""Auth 모듈 이벤트 페이로드"""

from pydantic import BaseModel, Field


class SocialLoginSuccessedPayload(BaseModel):
    """
    사용자 계정 요청 페이로드 (Auth -> User)
    """

    provider: str = Field(..., description="OAuth 제공자 (KAKAO, NAVER, GOOGLE)")
    provider_id: str = Field(..., description="제공자의 고유 사용자 ID")


class FindUserAccountResultPayload(BaseModel):
    """
    사용자 계정 결과 페이로드 (User → Auth)
    """
    
    user_account_id: int = Field(..., description="사용자 계정 ID")
