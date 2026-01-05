"""유저 태그 목록 Response Schema"""

from datetime import date
from pydantic import BaseModel, Field


class PrevTagResponse(BaseModel):
    """선수 태그 정보"""
    tag_id: int = Field(..., alias="tagId")
    tag_code: str = Field(..., alias="tagCode")
    tag_display_name: str = Field(..., alias="tagDisplayName")
    satisfied_yn: bool = Field(..., alias="satisfiedYn")

    class Config:
        populate_by_name = True


class RequiredStatResponse(BaseModel):
    """태그 해금 요구사항"""
    required_min_tier: str = Field(..., alias="requiredMinTier")
    prev_tags: list[PrevTagResponse] = Field(..., alias="prevTags")

    class Config:
        populate_by_name = True


class NextLevelStatResponse(BaseModel):
    """다음 레벨 요구사항"""
    next_level: str = Field(..., alias="nextLevel")
    solved_problem_count: int = Field(..., alias="solvedProblemCount")
    required_min_tier: str = Field(..., alias="requiredMinTier")
    higher_problem_tier: str = Field(..., alias="higherProblemTier")

    class Config:
        populate_by_name = True


class AccountStatResponse(BaseModel):
    """유저의 태그별 통계"""
    current_level: str = Field(..., alias="currentLevel")
    solved_problem_count: int = Field(..., alias="solvedProblemCount")
    required_min_tier: str | None = Field(None, alias="requiredMinTier")
    higher_problem_tier: str | None = Field(None, alias="higherProblemTier")
    last_solved_date: date | None = Field(None, alias="lastSolvedDate")

    class Config:
        populate_by_name = True


class TagAliasResponse(BaseModel):
    """태그 별칭"""
    alias: str

    class Config:
        populate_by_name = True


class TargetResponse(BaseModel):
    """목표 정보"""
    target_id: int = Field(..., alias="targetId")
    target_code: str = Field(..., alias="targetCode")
    target_display_name: str = Field(..., alias="targetDisplayName")

    class Config:
        populate_by_name = True


class UserTagDetailResponse(BaseModel):
    """유저 태그 상세 정보"""
    tag_id: int = Field(..., alias="tagId")
    tag_code: str = Field(..., alias="tagCode")
    tag_display_name: str = Field(..., alias="tagDisplayName")
    tag_targets: list[TargetResponse] = Field(..., alias="tagTargets")
    tag_aliases: list[TagAliasResponse] = Field(..., alias="tagAliases")
    required_stat: RequiredStatResponse | None = Field(None, alias="requiredStat")
    next_level_stat: NextLevelStatResponse | None = Field(None, alias="nextLevelStat")
    account_stat: AccountStatResponse = Field(..., alias="accountStat")
    locked_yn: bool = Field(..., alias="lockedYn")
    excluded_yn: bool = Field(..., alias="excludedYn")
    recommendation_yn: bool = Field(..., alias="recommendationYn")

    class Config:
        populate_by_name = True


class CategoryResponse(BaseModel):
    """태그 카테고리"""
    category_name: str = Field(..., alias="categoryName")
    tags: list[UserTagDetailResponse]

    class Config:
        populate_by_name = True


class UserTagsResponse(BaseModel):
    """유저 태그 목록 조회 응답"""
    categories: list[CategoryResponse]
    tags: list[UserTagDetailResponse]

    class Config:
        populate_by_name = True
