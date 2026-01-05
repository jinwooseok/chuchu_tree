"""월간 활동 데이터 쿼리 응답"""
from datetime import date
from pydantic import BaseModel, Field


class DailyActivityItemQuery(BaseModel):
    """일별 활동 항목 쿼리"""
    problem_id: int = Field(..., description="문제 ID")
    marked_date: date = Field(..., description="마킹 날짜")


class DailyActivityQuery(BaseModel):
    """일별 활동 쿼리"""
    target_date: date = Field(..., description="날짜")
    solved_problem_ids: list[int] = Field(default_factory=list, description="푼 문제 ID 목록")
    will_solve_problem_ids: list[int] = Field(default_factory=list, description="풀 예정 문제 ID 목록")


class MonthlyActivityDataQuery(BaseModel):
    """월간 활동 데이터 쿼리 응답"""
    daily_activities: list[DailyActivityQuery] = Field(..., description="일별 활동 목록")
    total_problem_count: int = Field(..., description="전체 문제 수")
