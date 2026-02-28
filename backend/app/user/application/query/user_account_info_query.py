from datetime import datetime
from pydantic import BaseModel, Field

from app.user.application.query.user_tags_query import TargetQuery

class GetUserAccountInfoQuery(BaseModel):
    """유저 계정 정보 조회 쿼리 응답"""
    user_account_id: int = Field(..., description="유저 계정 ID")
    provider: str = Field(..., description="소셜 로그인 제공자")
    targets: list[TargetQuery] = Field([], description="목표 목록")
    profile_image_url: str | None = Field(None, description="프로필 이미지 presigned URL")
    registered_at: datetime = Field(..., description="가입일")
    is_synced: bool = Field(False, description="배치 동기화 완료 여부")
