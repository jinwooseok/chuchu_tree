from pydantic import BaseModel, Field
from typing import List


class PrevTag(BaseModel):
    """선행 태그"""
    tag_id: int = Field(..., alias="tagId")
    tag_code: str = Field(..., alias="tagCode")
    tag_display_name: str = Field(..., alias="tagDisplayName")
    satisfied_yn: bool = Field(..., alias="satisfiedYn")

    class Config:
        populate_by_name = True


class RequiredStat(BaseModel):
    """필요 조건"""
    required_min_tier: str = Field(..., alias="requiredMinTier")
    prev_tags: List[PrevTag] = Field(..., alias="prevTags")

    class Config:
        populate_by_name = True


class NextLevelStat(BaseModel):
    """다음 레벨 조건"""
    next_level: str = Field(..., alias="nextLevel")
    solved_problem_count: int = Field(..., alias="solvedProblemCount")
    required_min_tier: str = Field(..., alias="requiredMinTier")
    higher_problem_tier: str = Field(..., alias="higherProblemTier")

    class Config:
        populate_by_name = True


class AccountStat(BaseModel):
    """계정 통계"""
    current_level: str = Field(..., alias="currentLevel")
    solved_problem_count: int = Field(..., alias="solvedProblemCount")
    required_min_tier: str = Field(..., alias="requiredMinTier")
    higher_problem_tier: str = Field(..., alias="higherProblemTier")
    last_solved_date: str | None = Field(None, alias="lastSolvedDate")

    class Config:
        populate_by_name = True


class UserTagItem(BaseModel):
    """유저 태그 항목"""
    tag_id: int = Field(..., alias="tagId")
    tag_code: str = Field(..., alias="tagCode")
    tag_display_name: str = Field(..., alias="tagDisplayName")
    required_stat: RequiredStat | None = Field(None, alias="requiredStat")
    next_level_stat: NextLevelStat | None = Field(None, alias="nextLevelStat")
    account_stat: AccountStat | None = Field(None, alias="accountStat")
    locked_yn: bool = Field(..., alias="locked_yn")
    excluded_yn: bool = Field(..., alias="excluded_yn")
    recommendation_yn: bool = Field(..., alias="recommandation_yn")

    class Config:
        populate_by_name = True


class TagCategory(BaseModel):
    """태그 카테고리"""
    category_name: str = Field(..., alias="categoryName")
    tags: List[UserTagItem]

    class Config:
        populate_by_name = True


class UserTagsResponse(BaseModel):
    """유저의 태그 목록 조회 응답"""
    categories: List[TagCategory]
    tags: List[UserTagItem]

    class Config:
        populate_by_name = True


class LevelStat(BaseModel):
    """레벨 통계"""
    level: str
    solved_problem_count: int = Field(..., alias="solvedProblemCount")
    required_min_tier: str = Field(..., alias="requiredMinTier")
    higher_problem_tier: str = Field(..., alias="higherProblemTier")

    class Config:
        populate_by_name = True


class AllTagItem(BaseModel):
    """전체 태그 항목"""
    tag_id: int = Field(..., alias="tagId")
    tag_code: str = Field(..., alias="tagCode")
    tag_display_name: str = Field(..., alias="tagDisplayName")
    required_stat: RequiredStat | None = Field(None, alias="requiredStat")
    level_stats: List[LevelStat] = Field(..., alias="levelStats")
    active_yn: bool = Field(..., alias="active_yn")

    class Config:
        populate_by_name = True


class AllTagsResponse(BaseModel):
    """전체 태그 목록 조회 응답"""
    tags: List[AllTagItem]

    class Config:
        populate_by_name = True
