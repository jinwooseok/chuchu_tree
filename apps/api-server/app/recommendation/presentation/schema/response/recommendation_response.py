from pydantic import BaseModel, Field, ConfigDict
from pydantic.alias_generators import to_camel
from typing import List, Any

from app.recommendation.application.query.recommend_problems_query import (
    RecommendProblemsQuery,
    RecommendedProblemQuery,
    RecommendReasonQuery,
    TagInfoQuery,
    TagAliasQuery,
    TagTargetQuery
)


class TagTarget(BaseModel):
    """태그 목표"""
    target_id: int = Field(..., alias="targetId")
    target_code: str = Field(..., alias="targetCode")
    target_display_name: str = Field(..., alias="targetDisplayName")

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True
    )

    @classmethod
    def from_query(cls, query: TagTargetQuery) -> "TagTarget":
        """Query 객체로부터 Response 생성"""
        return cls(
            target_id=query.target_id,
            target_code=query.target_code,
            target_display_name=query.target_display_name
        )


class TagAlias(BaseModel):
    """태그 별칭"""
    alias: str

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True
    )

    @classmethod
    def from_query(cls, query: TagAliasQuery) -> "TagAlias":
        """Query 객체로부터 Response 생성"""
        return cls(alias=query.alias)


class TagInfo(BaseModel):
    """태그 정보"""
    tag_id: int = Field(..., alias="tagId")
    tag_code: str = Field(..., alias="tagCode")
    tag_display_name: str = Field(..., alias="tagDisplayName")
    tag_targets: List[TagTarget] | None = Field(None, alias="tagTargets")
    tag_aliases: List[TagAlias] = Field(default_factory=list, alias="tagAliases")

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True
    )

    @classmethod
    def from_query(cls, query: TagInfoQuery) -> "TagInfo":
        """Query 객체로부터 Response 생성"""
        return cls(
            tag_id=query.tag_id,
            tag_code=query.tag_code,
            tag_display_name=query.tag_display_name,
            tag_targets=[TagTarget.from_query(t) for t in query.tag_targets] if query.tag_targets else None,
            tag_aliases=[TagAlias.from_query(a) for a in query.tag_aliases]
        )


class RecommendReason(BaseModel):
    """추천 이유"""
    reason: str
    additional_data: Any | None = Field(None, alias="additionalData")

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True
    )

    @classmethod
    def from_query(cls, query: RecommendReasonQuery) -> "RecommendReason":
        """Query 객체로부터 Response 생성"""
        return cls(
            reason=query.reason,
            additional_data=query.additional_data
        )


class RecommendedProblem(BaseModel):
    """추천 문제"""
    problem_id: int = Field(..., alias="problemId")
    problem_title: str = Field(..., alias="problemTitle")
    problem_tier_level: int = Field(..., alias="problemTierLevel")
    problem_tier_name: str = Field(..., alias="problemTierName")
    problem_class_level: int = Field(..., alias="problemClassLevel")
    recommend_reasons: List[RecommendReason] = Field(..., alias="recommandReasons")
    tags: List[TagInfo]

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True
    )

    @classmethod
    def from_query(cls, query: RecommendedProblemQuery) -> "RecommendedProblem":
        """Query 객체로부터 Response 생성"""
        return cls(
            problem_id=query.problem_id,
            problem_title=query.problem_title,
            problem_tier_level=query.problem_tier_level,
            problem_tier_name=query.problem_tier_name,
            problem_class_level=query.problem_class_level,
            recommend_reasons=[RecommendReason.from_query(r) for r in query.recommend_reasons],
            tags=[TagInfo.from_query(t) for t in query.tags]
        )


class RecommendationResponse(BaseModel):
    """문제 추천 응답"""
    problems: List[RecommendedProblem]

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True
    )

    @classmethod
    def from_query(cls, query: RecommendProblemsQuery) -> "RecommendationResponse":
        """Query 객체로부터 Response 생성"""
        return cls(
            problems=[RecommendedProblem.from_query(p) for p in query.problems]
        )
