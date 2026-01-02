from pydantic import BaseModel, Field
from typing import List, Any


class TagTarget(BaseModel):
    """태그 목표"""
    target_id: int = Field(..., alias="targetId")
    target_code: str = Field(..., alias="targetCode")
    target_display_name: str = Field(..., alias="targetDisplayName")

    class Config:
        populate_by_name = True


class TagAlias(BaseModel):
    """태그 별칭"""
    alias: str

    class Config:
        populate_by_name = True


class TagInfo(BaseModel):
    """태그 정보"""
    tag_id: int = Field(..., alias="tagId")
    tag_code: str = Field(..., alias="tagCode")
    tag_display_name: str = Field(..., alias="tagDisplayName")
    tag_target: List[TagTarget] | None = Field(None, alias="tagTarget")
    tag_aliases: List[TagAlias] = Field(default_factory=list, alias="tagAliases")

    class Config:
        populate_by_name = True


class RecommendReason(BaseModel):
    """추천 이유"""
    reason: str
    additional_data: Any | None = Field(None, alias="additionalData")

    class Config:
        populate_by_name = True


class RecommendedProblem(BaseModel):
    """추천 문제"""
    problem_id: int = Field(..., alias="problemId")
    problem_title: str = Field(..., alias="problemTitle")
    problem_tier_level: int = Field(..., alias="problemTierLevel")
    problem_tier_name: str = Field(..., alias="problemTierName")
    problem_class_level: int = Field(..., alias="problemClassLevel")
    recommend_reasons: List[RecommendReason] = Field(..., alias="recommandReasons")
    tags: List[TagInfo]

    class Config:
        populate_by_name = True


class RecommendationResponse(BaseModel):
    """문제 추천 응답"""
    problems: List[RecommendedProblem]

    class Config:
        populate_by_name = True
