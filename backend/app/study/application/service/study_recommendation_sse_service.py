import logging

from app.common.infra.event.decorators import event_handler, event_register_handlers
from app.study.domain.event.payloads import StudyRecommendationCompletedPayload
from app.study.infra.sse.study_sse_manager import StudySSEManager
from app.study.application.query.study_recommend_query import StudyRecommendProblemsQuery
from app.study.presentation.schema.response.study_recommend_response import StudyRecommendationResponse

logger = logging.getLogger(__name__)


@event_register_handlers()
class StudyRecommendationSSEService:
    def __init__(self, study_sse_manager: StudySSEManager):
        self.study_sse_manager = study_sse_manager

    @event_handler("STUDY_RECOMMENDATION_COMPLETED")
    async def handle_study_recommendation_completed(self, payload: StudyRecommendationCompletedPayload) -> None:
        try:
            query = StudyRecommendProblemsQuery(problems=payload.problems)
            data = StudyRecommendationResponse.from_query(query).model_dump(by_alias=True)
            await self.study_sse_manager.notify(
                study_id=payload.study_id,
                event_type="STUDY_RECOMMENDATION",
                payload=data,
                exclude_user_account_id=payload.requester_user_account_id,
            )
        except Exception as e:
            logger.error(f"[StudyRecommendationSSEService] STUDY_RECOMMENDATION_COMPLETED 처리 실패: {e}")
