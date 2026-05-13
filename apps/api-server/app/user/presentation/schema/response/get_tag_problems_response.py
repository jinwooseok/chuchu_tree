"""태그 별 푼 문제 조회 응답 스키마"""

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

from app.baekjoon.presentation.schema.response.get_monthly_problems_response import (
    ProblemInfoResponse,
    TagInfoResponse,
)
from app.user.application.query.tag_problems_query import TagProblemQuery, TagProblemsQuery


class TagProblemResponse(ProblemInfoResponse):
    """태그 별 푼 문제 응답 (solved_date 포함)"""
    solved_date: str | None = Field(None, description="가장 이른 solved 날짜 (YYYY-MM-DD), 없으면 null")

    @classmethod
    def from_query(cls, query: TagProblemQuery) -> "TagProblemResponse":
        return cls(
            problem_id=query.problem_id,
            problem_title=query.problem_title,
            problem_tier_level=query.problem_tier_level,
            problem_tier_name=query.problem_tier_name,
            problem_class_level=query.problem_class_level,
            tags=[TagInfoResponse.from_query(t) for t in query.tags],
            solved_date=query.solved_date,
        )


class GetTagProblemsResponse(BaseModel):
    """태그 별 푼 문제 조회 응답"""
    total_problem_count: int = Field(..., description="전체 문제 수")
    problems: list[TagProblemResponse] = Field(default_factory=list, description="푼 문제 목록")

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    @classmethod
    def from_query(cls, query: TagProblemsQuery) -> "GetTagProblemsResponse":
        return cls(
            total_problem_count=query.total_problem_count,
            problems=[TagProblemResponse.from_query(p) for p in query.problems],
        )
