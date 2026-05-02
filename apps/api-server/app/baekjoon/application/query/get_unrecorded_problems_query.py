from pydantic import BaseModel, Field

from app.problem.application.query.problems_info_query import ProblemInfoQuery


class GetUnrecordedProblemsQuery(BaseModel):
    """기록되지 않은 문제 목록 쿼리"""
    problems: list[ProblemInfoQuery] = Field(default_factory=list, description="기록되지 않은 문제 목록")