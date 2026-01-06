from pydantic import BaseModel, Field
from typing import List

from app.problem.application.query.problems_info_query import ProblemInfoQuery, TagInfoQuery


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
        
    @classmethod
    def from_query(cls, query: TagInfoQuery) -> "TagInfo":
        return cls(
            tagId=query.tag_id,
            tagCode=query.tag_code,
            tagDisplayName=query.tag_display_name,
            tagTarget=[
                TagTarget(
                    targetId=t.target_id,
                    targetCode=t.target_code,
                    targetDisplayName=t.target_display_name
                ) for t in query.tag_targets
            ],
            tagAliases=[TagAlias(alias=a.alias) for a in query.tag_aliases]
        )


class ProblemItem(BaseModel):
    """문제 항목"""
    problem_id: int = Field(..., alias="problemId")
    problem_title: str = Field(..., alias="problemTitle")
    problem_tier_level: int = Field(..., alias="problemTierLevel")
    problem_tier_name: str = Field(..., alias="problemTierName")
    problem_class_level: int | None = Field(..., alias="problemClassLevel")
    tags: list[TagInfo]

    class Config:
        populate_by_name = True

    @classmethod
    def from_query(cls, query: ProblemInfoQuery) -> "ProblemItem":
        return cls(
            problemId=query.problem_id,
            problemTitle=query.problem_title,
            problemTierLevel=query.problem_tier_level,
            problemTierName=query.problem_tier_name,
            problemClassLevel=query.problem_class_level,
            tags=[TagInfo.from_query(t) for t in query.tags]
        )
    
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
        
    @classmethod
    def from_queries(
        cls, 
        id_base_queries: list[ProblemInfoQuery], 
        title_base_queries: list[ProblemInfoQuery]
    ) -> "ProblemSearchResponse":
        return cls(
            problems=ProblemSearchResults(
                idBaseTotalCount=len(id_base_queries),
                titleBaseTotalCount=len(title_base_queries),
                idBase=[ProblemItem.from_query(q) for q in id_base_queries],
                titleBase=[ProblemItem.from_query(q) for q in title_base_queries]
            )
        )
