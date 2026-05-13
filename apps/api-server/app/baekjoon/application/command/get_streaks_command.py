from datetime import date
from pydantic import BaseModel, Field


class GetStreaksCommand(BaseModel):
    """스트릭 조회 명령"""
    user_account_id: int = Field(..., description="유저 계정 ID")
    start_date: date = Field(..., description="시작 날짜")
    end_date: date = Field(..., description="종료 날짜")
