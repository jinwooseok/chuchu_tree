from dataclasses import dataclass
from datetime import datetime

from app.common.domain.vo.identifiers import RecommendationHistoryId, StudyId, UserAccountId
from app.recommendation.domain.vo.recommendation_params import RecommendationParams


@dataclass
class RecommendationHistory:
    """Entity - 문제 추천 히스토리 (추천 시점의 문제 스냅샷 저장)"""
    recommendation_history_id: RecommendationHistoryId | None
    requester_user_account_id: UserAccountId
    study_id: StudyId | None
    params: RecommendationParams
    recommended_problems: list[dict]  # RecommendedProblemQuery 직렬화 JSON
    created_at: datetime

    @staticmethod
    def create(
        requester_user_account_id: UserAccountId,
        params: RecommendationParams,
        recommended_problems: list[dict],
        study_id: StudyId | None = None,
    ) -> "RecommendationHistory":
        return RecommendationHistory(
            recommendation_history_id=None,
            requester_user_account_id=requester_user_account_id,
            study_id=study_id,
            params=params,
            recommended_problems=recommended_problems,
            created_at=datetime.now(),
        )
