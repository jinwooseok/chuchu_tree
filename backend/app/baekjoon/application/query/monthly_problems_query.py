"""월간 문제 쿼리 응답"""
from datetime import date
from pydantic import BaseModel, Field

from app.problem.application.query.problems_info_query import ProblemInfoQuery


class RepresentativeTagSummary(BaseModel):
    """대표 태그 요약 정보"""
    tag_id: int = Field(..., description="태그 ID")
    tag_code: str = Field(..., description="태그 코드")
    tag_display_name: str = Field(..., description="태그 표시 이름")


class SolvedProblemQuery(ProblemInfoQuery):
    """푼 문제 쿼리 (realSolvedYn, 대표태그 포함)"""
    real_solved_yn: bool = Field(..., description="실제 solved.ac에서 푼 문제 여부")
    representative_tag: RepresentativeTagSummary | None = Field(None, description="대표 태그 정보")


class WillSolveProblemQuery(ProblemInfoQuery):
    """풀 예정 문제 쿼리 (대표태그 포함)"""
    representative_tag: RepresentativeTagSummary | None = Field(None, description="대표 태그 정보")


class MonthlyDayDataQuery(BaseModel):
    """월간 일별 데이터 쿼리"""
    target_date: str = Field(..., description="날짜 (YYYY-MM-DD)")
    solved_problem_count: int = Field(..., description="푼 문제 수")
    will_solve_problem_count: int = Field(..., description="풀 예정 문제 수")
    solved_problems: list[SolvedProblemQuery] = Field(default_factory=list, description="푼 문제 목록")
    will_solve_problems: list[WillSolveProblemQuery] = Field(default_factory=list, description="풀 예정 문제 목록")


class MonthlyProblemsQuery(BaseModel):
    """월간 문제 쿼리 응답"""
    total_problem_count: int = Field(..., description="전체 문제 수")
    monthly_data: list[MonthlyDayDataQuery] = Field(..., description="월간 일별 데이터")
