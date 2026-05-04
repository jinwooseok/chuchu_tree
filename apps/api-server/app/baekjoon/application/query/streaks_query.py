from datetime import date
from pydantic import BaseModel, Field


class StreakItemQuery(BaseModel):
    """스트릭 항목 쿼리"""
    problem_history_id: int | None = Field(None, description="문제 연관 ID")
    streak_date: date = Field(..., description="스트릭 날짜")
    solved_count: int = Field(..., description="해당 날짜에 푼 문제 수")


class StreaksQuery(BaseModel):
    """스트릭 목록 쿼리"""
    bj_account_id: str = Field(..., description="백준 계정 ID")
    streaks: list[StreakItemQuery] = Field(..., description="스트릭 목록")
    total_count: int = Field(..., description="전체 스트릭 수")
