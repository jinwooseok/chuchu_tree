from dataclasses import dataclass
from datetime import datetime

from pydantic import BaseModel, Field

class TagInfoQuery(BaseModel):
    """태그 정보 쿼리"""
    tag_id: int = Field(..., description="태그 ID")
    tag_code: str = Field(..., description="태그 코드")
    tag_display_name: str = Field(..., description="태그 표시 이름")

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

@dataclass
class BannedProblemsQuery:
    banned_problem_list: list[ProblemInfoQuery]

@dataclass
class BannedTagsQuery:
    banned_tag_list: list[TagInfoQuery]