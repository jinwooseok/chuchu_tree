from dataclasses import dataclass, field

from app.recommendation.application.query.recommend_problems_query import RecommendedProblemQuery


@dataclass
class RecommendationParamsQuery:
    """추천 파라미터 쿼리"""
    count: int
    exclusion_mode: str
    level_filter_codes: list[str] | None
    tag_filter_codes: list[str] | None
    target_user_account_id: int | None
    recommend_all_unsolved: bool


@dataclass
class RecommendationHistoryItemQuery:
    """추천 히스토리 단건 쿼리"""
    recommendation_history_id: int
    requester_user_account_id: int
    study_id: int | None
    params: RecommendationParamsQuery
    recommended_problems: list[RecommendedProblemQuery]
    created_at: str  # ISO 8601 string (rule: response에 datetime 사용 금지)


@dataclass
class RecommendationHistoryQuery:
    """추천 히스토리 목록 쿼리"""
    items: list[RecommendationHistoryItemQuery] = field(default_factory=list)
    next_cursor: int | None = None
    has_next: bool = False
