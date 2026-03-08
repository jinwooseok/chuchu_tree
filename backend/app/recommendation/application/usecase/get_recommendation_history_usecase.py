from app.common.domain.vo.identifiers import UserAccountId
from app.core.database import transactional
from app.recommendation.application.query.recommend_problems_query import RecommendedProblemQuery
from app.recommendation.application.query.recommendation_history_query import (
    RecommendationHistoryItemQuery,
    RecommendationHistoryQuery,
    RecommendationParamsQuery,
)
from app.recommendation.domain.repository.recommendation_history_repository import (
    RecommendationHistoryRepository,
)


class GetRecommendationHistoryUsecase:
    """개인 추천 히스토리 조회 (study_id IS NULL)"""

    def __init__(self, recommendation_history_repository: RecommendationHistoryRepository):
        self.recommendation_history_repository = recommendation_history_repository

    @transactional(readonly=True)
    async def execute(
        self, user_account_id: int, page: int = 1, size: int = 10
    ) -> RecommendationHistoryQuery:
        histories = await self.recommendation_history_repository.find_by_user_account_id(
            UserAccountId(user_account_id), page=page, size=size
        )
        has_next = len(histories) > size
        items = [
            RecommendationHistoryItemQuery(
                recommendation_history_id=h.recommendation_history_id.value,
                requester_user_account_id=h.requester_user_account_id.value,
                study_id=h.study_id.value if h.study_id else None,
                params=RecommendationParamsQuery(
                    count=h.params.count,
                    exclusion_mode=h.params.exclusion_mode,
                    level_filter_codes=h.params.level_filter_codes,
                    tag_filter_codes=h.params.tag_filter_codes,
                    target_user_account_id=h.params.target_user_account_id,
                    recommend_all_unsolved=h.params.recommend_all_unsolved,
                ),
                recommended_problems=[RecommendedProblemQuery.model_validate(p) for p in h.recommended_problems],
                created_at=h.created_at.isoformat(),
            )
            for h in histories[:size]
        ]
        return RecommendationHistoryQuery(items=items, page=page, size=size, has_next=has_next)
