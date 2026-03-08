from app.common.domain.vo.identifiers import RecommendationHistoryId, StudyId, UserAccountId
from app.recommendation.domain.entity.recommendation_history import RecommendationHistory
from app.recommendation.domain.vo.recommendation_params import RecommendationParams
from app.recommendation.infra.model.recommendation_history import RecommendationHistoryModel


class RecommendationHistoryMapper:

    @staticmethod
    def to_entity(model: RecommendationHistoryModel | None) -> RecommendationHistory | None:
        if not model:
            return None
        return RecommendationHistory(
            recommendation_history_id=RecommendationHistoryId(model.recommendation_history_id),
            requester_user_account_id=UserAccountId(model.requester_user_account_id),
            study_id=StudyId(model.study_id) if model.study_id is not None else None,
            params=RecommendationParams.from_dict(model.params),
            recommended_problems=model.recommended_problems,
            created_at=model.created_at,
        )

    @staticmethod
    def to_model(entity: RecommendationHistory) -> RecommendationHistoryModel:
        return RecommendationHistoryModel(
            recommendation_history_id=(
                entity.recommendation_history_id.value
                if entity.recommendation_history_id
                else None
            ),
            requester_user_account_id=entity.requester_user_account_id.value,
            study_id=entity.study_id.value if entity.study_id else None,
            params=entity.params.to_dict(),
            recommended_problems=entity.recommended_problems,
            created_at=entity.created_at,
        )
