"""월간 활동 데이터 조회 요청 페이로드"""
from pydantic import BaseModel, Field


class GetMonthlyActivityDataPayload(BaseModel):
    """월간 활동 데이터 조회 요청 페이로드"""
    user_account_id: int = Field(..., description="유저 계정 ID")
    year: int = Field(..., description="연도")
    month: int = Field(..., ge=1, le=12, description="월 (1-12)")
