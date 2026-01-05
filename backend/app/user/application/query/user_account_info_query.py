from datetime import datetime
from pydantic import BaseModel, Field


class GetUserAccountInfoQuery(BaseModel):
    """유저 계정 정보 조회 쿼리 응답"""
    user_account_id: int = Field(..., description="유저 계정 ID")
    provider: str = Field(..., description="소셜 로그인 제공자")
    profile_image: str | None = Field(None, description="프로필 이미지 URL")
    registered_at: datetime = Field(..., description="가입일")
