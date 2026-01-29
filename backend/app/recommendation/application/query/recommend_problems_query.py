"""문제 추천 Query 객체"""

from pydantic import BaseModel, Field


class TagTargetQuery(BaseModel):
    """태그 목표 쿼리"""
    target_id: int = Field(..., description="목표 ID")
    target_code: str = Field(..., description="목표 코드")
    target_display_name: str = Field(..., description="목표 표시 이름")


class TagAliasQuery(BaseModel):
    """태그 별칭 쿼리"""
    alias: str = Field(..., description="별칭")


class TagInfoQuery(BaseModel):
    """태그 정보 쿼리"""
    tag_id: int = Field(..., description="태그 ID")
    tag_code: str = Field(..., description="태그 코드")
    tag_display_name: str = Field(..., description="태그 표시 이름")
    tag_targets: list[TagTargetQuery] | None = Field(None, description="태그 목표 목록")
    tag_aliases: list[TagAliasQuery] = Field(default_factory=list, description="태그 별칭 목록")


class RecommendReasonQuery(BaseModel):
    """추천 이유 쿼리"""
    reason: str = Field(..., description="추천 이유")
    additional_data: dict | None = Field(None, description="추가 데이터")


class RecommendedProblemQuery(BaseModel):
    """추천 문제 쿼리"""
    problem_id: int = Field(..., description="문제 ID")
    problem_title: str = Field(..., description="문제 제목")
    problem_tier_level: int = Field(..., description="문제 티어 레벨")
    problem_tier_name: str = Field(..., description="문제 티어 이름")
    problem_class_level: int = Field(..., description="문제 클래스 레벨")
    recommend_reasons: list[RecommendReasonQuery] = Field(..., description="추천 이유 목록")
    tags: list[TagInfoQuery] = Field(..., description="태그 목록")


class RecommendProblemsQuery(BaseModel):
    """문제 추천 쿼리"""
    problems: list[RecommendedProblemQuery] = Field(..., description="추천 문제 목록")
