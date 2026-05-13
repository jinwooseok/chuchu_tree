from pydantic import BaseModel, Field


class GetUserAccountInfoPayload(BaseModel):
    """유저 계정 정보 조회 요청 페이로드"""
    user_account_id: int = Field(..., description="유저 계정 ID")
