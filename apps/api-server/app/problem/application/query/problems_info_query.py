"""문제 정보 쿼리 응답"""
from pydantic import BaseModel, Field


class TagAliasQuery(BaseModel):
    """태그 별칭 쿼리"""
    alias: str = Field(..., description="별칭")


class TagTargetQuery(BaseModel):
    """태그 목표 쿼리"""
    target_id: int = Field(..., description="목표 ID")
    target_code: str = Field(..., description="목표 코드")
    target_display_name: str = Field(..., description="목표 표시 이름")


class TagInfoQuery(BaseModel):
    """태그 정보 쿼리"""
    tag_id: int = Field(..., description="태그 ID")
    tag_code: str = Field(..., description="태그 코드")
    tag_display_name: str = Field(..., description="태그 표시 이름")
    tag_aliases: list[TagAliasQuery] = Field(default_factory=list, description="태그 별칭 목록")
    tag_targets: list[TagTargetQuery] = Field(default_factory=list, description="태그 목표 목록")


class ProblemInfoQuery(BaseModel):
    """문제 정보 쿼리"""
    problem_id: int = Field(..., description="문제 ID")
    problem_title: str = Field(..., description="문제 제목")
    problem_tier_level: int = Field(..., description="문제 티어 레벨")
    problem_tier_name: str = Field(..., description="문제 티어 이름")
    problem_class_level: int | None = Field(None, description="문제 클래스 레벨")
    tags: list[TagInfoQuery] = Field(default_factory=list, description="태그 목록")


class ProblemsInfoQuery(BaseModel):
    """문제 정보 목록 쿼리 응답"""
    problems: dict[int, ProblemInfoQuery] = Field(..., description="문제 정보 맵 (problem_id -> ProblemInfoQuery)")
