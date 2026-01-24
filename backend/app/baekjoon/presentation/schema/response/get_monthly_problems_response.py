"""월간 문제 조회 응답 스키마"""
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

from app.baekjoon.application.query.monthly_problems_query import (
    MonthlyDayDataQuery,
    MonthlyProblemsQuery,
    RepresentativeTagSummary,
    SolvedProblemQuery,
    WillSolveProblemQuery
)
from app.problem.application.query.problems_info_query import (
    ProblemInfoQuery,
    TagAliasQuery,
    TagInfoQuery,
    TagTargetQuery
)


class TagAliasResponse(BaseModel):
    """태그 별칭 응답"""
    alias: str = Field(..., description="별칭")

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True
    )

    @classmethod
    def from_query(cls, query: TagAliasQuery) -> "TagAliasResponse":
        return cls(alias=query.alias)


class TagTargetResponse(BaseModel):
    """태그 목표 응답"""
    target_id: int = Field(..., description="목표 ID")
    target_code: str = Field(..., description="목표 코드")
    target_display_name: str = Field(..., description="목표 표시 이름")

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True
    )

    @classmethod
    def from_query(cls, query: TagTargetQuery) -> "TagTargetResponse":
        return cls(
            target_id=query.target_id,
            target_code=query.target_code,
            target_display_name=query.target_display_name
        )


class TagInfoResponse(BaseModel):
    """태그 정보 응답"""
    tag_id: int = Field(..., description="태그 ID")
    tag_code: str = Field(..., description="태그 코드")
    tag_display_name: str = Field(..., description="태그 표시 이름")
    tag_aliases: list[TagAliasResponse] = Field(default_factory=list, description="태그 별칭 목록")
    tag_targets: list[TagTargetResponse] = Field(default_factory=list, description="태그 목표 목록")

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True
    )

    @classmethod
    def from_query(cls, query: TagInfoQuery) -> "TagInfoResponse":
        return cls(
            tag_id=query.tag_id,
            tag_code=query.tag_code,
            tag_display_name=query.tag_display_name,
            tag_aliases=[TagAliasResponse.from_query(a) for a in query.tag_aliases],
            tag_targets=[TagTargetResponse.from_query(t) for t in query.tag_targets]
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


class RepresentativeTagSummaryResponse(BaseModel):
    """대표 태그 요약 응답"""
    tag_id: int = Field(..., description="태그 ID")
    tag_code: str = Field(..., description="태그 코드")
    tag_display_name: str = Field(..., description="태그 표시 이름")

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True
    )

    @classmethod
    def from_query(cls, query: RepresentativeTagSummary) -> "RepresentativeTagSummaryResponse":
        return cls(
            tag_id=query.tag_id,
            tag_code=query.tag_code,
            tag_display_name=query.tag_display_name
        )


class SolvedProblemResponse(ProblemInfoResponse):
    """푼 문제 응답 (realSolvedYn, 대표태그 포함)"""
    real_solved_yn: bool = Field(..., description="실제 solved.ac에서 푼 문제 여부")
    representative_tag: RepresentativeTagSummaryResponse | None = Field(None, description="대표 태그 정보")

    @classmethod
    def from_query(cls, query: SolvedProblemQuery) -> "SolvedProblemResponse":
        rep_tag = RepresentativeTagSummaryResponse.from_query(query.representative_tag) if query.representative_tag else None
        return cls(
            problem_id=query.problem_id,
            problem_title=query.problem_title,
            problem_tier_level=query.problem_tier_level,
            problem_tier_name=query.problem_tier_name,
            problem_class_level=query.problem_class_level,
            tags=[TagInfoResponse.from_query(t) for t in query.tags],
            real_solved_yn=query.real_solved_yn,
            representative_tag=rep_tag
        )


class WillSolveProblemResponse(ProblemInfoResponse):
    """풀 예정 문제 응답 (대표태그 포함)"""
    representative_tag: RepresentativeTagSummaryResponse | None = Field(None, description="대표 태그 정보")

    @classmethod
    def from_query(cls, query: WillSolveProblemQuery) -> "WillSolveProblemResponse":
        rep_tag = RepresentativeTagSummaryResponse.from_query(query.representative_tag) if query.representative_tag else None
        return cls(
            problem_id=query.problem_id,
            problem_title=query.problem_title,
            problem_tier_level=query.problem_tier_level,
            problem_tier_name=query.problem_tier_name,
            problem_class_level=query.problem_class_level,
            tags=[TagInfoResponse.from_query(t) for t in query.tags],
            representative_tag=rep_tag
        )


class MonthlyDayDataResponse(BaseModel):
    """월간 일별 데이터 응답"""
    target_date: str = Field(..., description="날짜 (YYYY-MM-DD)")
    solved_problem_count: int = Field(..., description="푼 문제 수")
    will_solve_problem_count: int = Field(..., description="풀 예정 문제 수")
    solved_problems: list[SolvedProblemResponse] = Field(default_factory=list, description="푼 문제 목록")
    will_solve_problems: list[WillSolveProblemResponse] = Field(default_factory=list, description="풀 예정 문제 목록")

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True
    )

    @classmethod
    def from_query(cls, query: MonthlyDayDataQuery) -> "MonthlyDayDataResponse":
        return cls(
            target_date=query.target_date,
            solved_problem_count=query.solved_problem_count,
            will_solve_problem_count=query.will_solve_problem_count,
            solved_problems=[SolvedProblemResponse.from_query(p) for p in query.solved_problems],
            will_solve_problems=[WillSolveProblemResponse.from_query(p) for p in query.will_solve_problems]
        )


class GetMonthlyProblemsResponse(BaseModel):
    """월간 문제 조회 응답"""
    total_problem_count: int = Field(..., description="전체 문제 수")
    monthly_data: list[MonthlyDayDataResponse] = Field(..., description="월간 일별 데이터")

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True
    )

    @classmethod
    def from_query(cls, query: MonthlyProblemsQuery) -> "GetMonthlyProblemsResponse":
        return cls(
            total_problem_count=query.total_problem_count,
            monthly_data=[MonthlyDayDataResponse.from_query(d) for d in query.monthly_data]
        )
