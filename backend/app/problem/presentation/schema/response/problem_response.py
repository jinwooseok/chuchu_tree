from pydantic import BaseModel, Field
from typing import List


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


class ProblemItem(BaseModel):
    """문제 항목"""
    problem_id: int = Field(..., alias="problemId")
    problem_title: str = Field(..., alias="problemTitle")
    problem_tier_level: int = Field(..., alias="problemTierLevel")
    problem_tier_name: str = Field(..., alias="problemTierName")
    problem_class_level: int = Field(..., alias="problemClassLevel")
    tags: List[TagInfo]

    class Config:
        populate_by_name = True


class ProblemSearchResults(BaseModel):
    """문제 검색 결과"""
    id_base_total_count: int = Field(..., alias="idBaseTotalCount")
    title_base_total_count: int = Field(..., alias="titleBaseTotalCount")
    id_base: List[ProblemItem] = Field(..., alias="idBase")
    title_base: List[ProblemItem] = Field(..., alias="titleBase")

    class Config:
        populate_by_name = True


class ProblemSearchResponse(BaseModel):
    """문제 검색 응답"""
    problems: ProblemSearchResults

    class Config:
        populate_by_name = True
