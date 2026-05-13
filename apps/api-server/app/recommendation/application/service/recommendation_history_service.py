import logging

from app.common.domain.vo.identifiers import StudyId, UserAccountId
from app.common.infra.event.decorators import event_handler, event_register_handlers
from app.core.database import transactional
from app.recommendation.domain.entity.recommendation_history import RecommendationHistory
from app.recommendation.domain.event.payloads import RecommendationCompletedPayload
from app.recommendation.domain.repository.recommendation_history_repository import (
    RecommendationHistoryRepository,
)
from app.recommendation.domain.vo.recommendation_params import RecommendationParams
from app.user.application.command.user_account_command import DeleteUserAccountCommand

logger = logging.getLogger(__name__)


@event_register_handlers()
class RecommendationHistoryService:

    def __init__(self, recommendation_history_repository: RecommendationHistoryRepository):
        self.recommendation_history_repository = recommendation_history_repository

    @event_handler("RECOMMENDATION_COMPLETED")
    @transactional
    async def save_history(self, payload: RecommendationCompletedPayload) -> None:
        history = RecommendationHistory.create(
            requester_user_account_id=UserAccountId(payload.requester_user_account_id),
            study_id=StudyId(payload.study_id) if payload.study_id is not None else None,
            params=RecommendationParams(
                count=payload.count,
                exclusion_mode=payload.exclusion_mode,
                level_filter_codes=payload.level_filter_codes,
                tag_filter_codes=payload.tag_filter_codes,
                target_user_account_id=payload.target_user_account_id,
                recommend_all_unsolved=payload.recommend_all_unsolved,
            ),
            recommended_problems=[p.model_dump() for p in payload.recommended_problems],
        )
        await self.recommendation_history_repository.save(history)
        logger.info(
            f"[RecommendationHistoryService] 히스토리 저장 완료: "
            f"user={payload.requester_user_account_id}, study={payload.study_id}"
        )

    @event_handler("USER_ACCOUNT_WITHDRAWAL_REQUESTED")
    @transactional
    async def delete_history(self, command: DeleteUserAccountCommand) -> None:
        await self.recommendation_history_repository.delete_by_user_account_id(
            UserAccountId(command.user_account_id)
        )
        logger.info(
            f"[RecommendationHistoryService] 추천 히스토리 삭제 완료: "
            f"user={command.user_account_id}"
        )
