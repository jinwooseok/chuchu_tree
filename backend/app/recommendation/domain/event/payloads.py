from pydantic import BaseModel

from app.recommendation.application.query.recommend_problems_query import RecommendedProblemQuery


class RecommendationCompletedPayload(BaseModel):
    requester_user_account_id: int
    recommended_problems: list[RecommendedProblemQuery]
    count: int
    exclusion_mode: str
    level_filter_codes: list[str] | None = None
    tag_filter_codes: list[str] | None = None
    study_id: int | None = None
    target_user_account_id: int | None = None
    recommend_all_unsolved: bool = False
