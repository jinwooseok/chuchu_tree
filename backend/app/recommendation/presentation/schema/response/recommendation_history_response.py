from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

from app.recommendation.application.query.recommendation_history_query import (
    RecommendationHistoryItemQuery,
    RecommendationHistoryQuery,
    RecommendationParamsQuery,
)
from app.recommendation.presentation.schema.response.recommendation_response import RecommendedProblem


class RecommendationParamsResponse(BaseModel):
    count: int
    exclusion_mode: str
    level_filter_codes: list[str] | None
    tag_filter_codes: list[str] | None
    target_user_account_id: int | None
    recommend_all_unsolved: bool

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    @classmethod
    def from_query(cls, query: RecommendationParamsQuery) -> "RecommendationParamsResponse":
        return cls(
            count=query.count,
            exclusion_mode=query.exclusion_mode,
            level_filter_codes=query.level_filter_codes,
            tag_filter_codes=query.tag_filter_codes,
            target_user_account_id=query.target_user_account_id,
            recommend_all_unsolved=query.recommend_all_unsolved,
        )


class RecommendationHistoryItemResponse(BaseModel):
    recommendation_history_id: int
    requester_user_account_id: int
    study_id: int | None
    params: RecommendationParamsResponse
    recommended_problems: list[RecommendedProblem]
    created_at: str

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    @classmethod
    def from_query(cls, query: RecommendationHistoryItemQuery) -> "RecommendationHistoryItemResponse":
        return cls(
            recommendation_history_id=query.recommendation_history_id,
            requester_user_account_id=query.requester_user_account_id,
            study_id=query.study_id,
            params=RecommendationParamsResponse.from_query(query.params),
            recommended_problems=[RecommendedProblem.from_query(p) for p in query.recommended_problems],
            created_at=query.created_at,
        )


class RecommendationHistoryResponse(BaseModel):
    items: list[RecommendationHistoryItemResponse]
    next_cursor: int | None
    has_next: bool

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    @classmethod
    def from_query(cls, query: RecommendationHistoryQuery) -> "RecommendationHistoryResponse":
        return cls(
            items=[RecommendationHistoryItemResponse.from_query(item) for item in query.items],
            next_cursor=query.next_cursor,
            has_next=query.has_next,
        )
