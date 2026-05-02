from datetime import date
from pydantic import BaseModel, Field


class GetStreaksRequest(BaseModel):
    """스트릭 조회 요청"""
    start_date: date = Field(..., description="시작 날짜")
    end_date: date = Field(..., description="종료 날짜")
