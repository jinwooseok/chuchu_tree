from dataclasses import dataclass

from app.recommendation.domain.vo.recommendation_params import RecommendationParams


@dataclass
class SaveRecommendationHistoryCommand:
    requester_user_account_id: int
    params: RecommendationParams
    recommended_problem_ids: list[int]
    study_id: int | None = None
