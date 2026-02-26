"""태그 별 푼 문제 조회 Query"""

from pydantic import BaseModel, Field

from app.problem.application.query.problems_info_query import ProblemInfoQuery


class TagProblemQuery(ProblemInfoQuery):
    """태그 별 푼 문제 쿼리 (solved_date 포함)"""
    solved_date: str | None = Field(None, description="가장 이른 solved 날짜 (YYYY-MM-DD), 없으면 null")


class TagProblemsQuery(BaseModel):
    """태그 별 푼 문제 목록 쿼리"""
    total_problem_count: int = Field(..., description="전체 문제 수")
    problems: list[TagProblemQuery] = Field(default_factory=list, description="푼 문제 목록")
