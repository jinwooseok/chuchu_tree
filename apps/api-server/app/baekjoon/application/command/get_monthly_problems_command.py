"""월간 문제 조회 명령"""
from pydantic import BaseModel, Field


class GetMonthlyProblemsCommand(BaseModel):
    """월간 문제 조회 명령"""
    user_account_id: int = Field(..., description="유저 계정 ID")
    year: int = Field(..., ge=2020, description="년도 (2020-)")
    month: int = Field(..., ge=1, le=12, description="월 (1-12)")
