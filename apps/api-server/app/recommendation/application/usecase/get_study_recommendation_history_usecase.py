from app.common.domain.vo.identifiers import StudyId, UserAccountId
from app.core.database import transactional
from app.core.error_codes import ErrorCode
from app.core.exception import APIException
from app.recommendation.application.query.recommend_problems_query import RecommendedProblemQuery
from app.recommendation.application.query.recommendation_history_query import (
    RecommendationHistoryItemQuery,
    RecommendationHistoryQuery,
    RecommendationParamsQuery,
)
from app.recommendation.domain.repository.recommendation_history_repository import (
    RecommendationHistoryRepository,
)
from app.study.domain.repository.study_repository import StudyRepository


class GetStudyRecommendationHistoryUsecase:
    """스터디 추천 히스토리 조회 (스터디 멤버만 조회 가능)"""

    def __init__(
        self,
        recommendation_history_repository: RecommendationHistoryRepository,
        study_repository: StudyRepository,
    ):
        self.recommendation_history_repository = recommendation_history_repository
        self.study_repository = study_repository

    @transactional(readonly=True)
    async def execute(
        self,
        study_id: int,
        requester_user_account_id: int,
        user_account_id: int | None = None,
        page: int = 1,
        size: int = 10,
    ) -> RecommendationHistoryQuery:
        study = await self.study_repository.find_by_id(StudyId(study_id))
        if study is None:
            raise APIException(ErrorCode.STUDY_NOT_FOUND)
        if not study.is_member(UserAccountId(requester_user_account_id)):
            raise APIException(ErrorCode.STUDY_NOT_MEMBER)

        histories = await self.recommendation_history_repository.find_by_study_id(
            StudyId(study_id),
            UserAccountId(user_account_id) if user_account_id is not None else None,
            page=page,
            size=size,
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
