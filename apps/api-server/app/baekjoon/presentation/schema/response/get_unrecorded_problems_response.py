"""기록되지 않은 문제 조회 응답 스키마"""
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

from app.baekjoon.application.query.get_unrecorded_problems_query import GetUnrecordedProblemsQuery
from app.problem.application.query.problems_info_query import (
    ProblemInfoQuery,
    TagAliasQuery,
    TagInfoQuery,
    TagTargetQuery
)

class TagInfoResponse(BaseModel):
    """태그 정보 응답"""
    tag_id: int = Field(..., description="태그 ID")
    tag_code: str = Field(..., description="태그 코드")
    tag_display_name: str = Field(..., description="태그 표시 이름")

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True
    )

    @classmethod
    def from_query(cls, query: TagInfoQuery) -> "TagInfoResponse":
        return cls(
            tag_id=query.tag_id,
            tag_code=query.tag_code,
            tag_display_name=query.tag_display_name
        )


class ProblemInfoResponse(BaseModel):
    """문제 정보 응답"""
    problem_id: int = Field(..., description="문제 ID")
    problem_title: str = Field(..., description="문제 제목")
    problem_tier_level: int = Field(..., description="문제 티어 레벨")
    problem_tier_name: str = Field(..., description="문제 티어 이름")
    problem_class_level: int | None = Field(None, description="문제 클래스 레벨")
    tags: list[TagInfoResponse] = Field(default_factory=list, description="태그 목록")

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True
    )

    @classmethod
    def from_query(cls, query: ProblemInfoQuery) -> "ProblemInfoResponse":
        return cls(
            problem_id=query.problem_id,
            problem_title=query.problem_title,
            problem_tier_level=query.problem_tier_level,
            problem_tier_name=query.problem_tier_name,
            problem_class_level=query.problem_class_level,
            tags=[TagInfoResponse.from_query(t) for t in query.tags]
        )


class GetUnrecordedProblemsResponse(BaseModel):
    """기록되지 않은 문제 조회 응답"""
    counts: int = Field(default=0, description="총 개수")
    problems: list[ProblemInfoResponse] = Field(default_factory=list, description="기록되지 않은 문제 목록")

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True
    )

    @classmethod
    def from_query(cls, query: GetUnrecordedProblemsQuery) -> "GetUnrecordedProblemsResponse":
        return cls(
            counts=len(query.problems),
            problems=[ProblemInfoResponse.from_query(p) for p in query.problems]
        )
