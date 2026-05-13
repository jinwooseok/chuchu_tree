"""월간 활동 데이터 쿼리 응답"""
from datetime import date
from pydantic import BaseModel, Field


class ProblemActivityInfo(BaseModel):
    """문제별 활동 정보 (대표 태그 ID 포함)"""
    problem_id: int = Field(..., description="문제 ID")
    representative_tag_id: int | None = Field(None, description="대표 태그 ID")


class DailyActivityQuery(BaseModel):
    """일별 활동 쿼리"""
    target_date: date = Field(..., description="날짜")
    solved_problems: list[ProblemActivityInfo] = Field(default_factory=list, description="푼 문제 목록")
    will_solve_problems: list[ProblemActivityInfo] = Field(default_factory=list, description="풀 예정 문제 목록")


class MonthlyActivityDataQuery(BaseModel):
    """월간 활동 데이터 쿼리 응답"""
    daily_activities: list[DailyActivityQuery] = Field(..., description="일별 활동 목록")
    total_problem_count: int = Field(..., description="전체 문제 수")
