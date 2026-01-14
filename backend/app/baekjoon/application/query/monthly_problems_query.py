"""월간 문제 쿼리 응답"""
from datetime import date
from pydantic import BaseModel, Field

from app.problem.application.query.problems_info_query import ProblemInfoQuery


class SolvedProblemQuery(ProblemInfoQuery):
    """푼 문제 쿼리 (realSolvedYn 포함)"""
    real_solved_yn: bool = Field(..., description="실제 solved.ac에서 푼 문제 여부")


class MonthlyDayDataQuery(BaseModel):
    """월간 일별 데이터 쿼리"""
    target_date: str = Field(..., description="날짜 (YYYY-MM-DD)")
    solved_problem_count: int = Field(..., description="푼 문제 수")
    will_solve_problem_count: int = Field(..., description="풀 예정 문제 수")
    solved_problems: list[SolvedProblemQuery] = Field(default_factory=list, description="푼 문제 목록")
    will_solve_problems: list[ProblemInfoQuery] = Field(default_factory=list, description="풀 예정 문제 목록")


class MonthlyProblemsQuery(BaseModel):
    """월간 문제 쿼리 응답"""
    total_problem_count: int = Field(..., description="전체 문제 수")
    monthly_data: list[MonthlyDayDataQuery] = Field(..., description="월간 일별 데이터")
