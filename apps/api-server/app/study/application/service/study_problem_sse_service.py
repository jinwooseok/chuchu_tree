import logging

from app.common.infra.event.decorators import event_handler, event_register_handlers
from app.study.domain.event.payloads import StudyProblemAssignedPayload
from app.study.infra.sse.study_sse_manager import StudySSEManager
from app.study.presentation.schema.response.study_problem_sse_response import StudyProblemAssignedSSEResponse

logger = logging.getLogger(__name__)


@event_register_handlers()
class StudyProblemSSEService:
    def __init__(self, study_sse_manager: StudySSEManager):
        self.study_sse_manager = study_sse_manager

    @event_handler("STUDY_PROBLEM_ASSIGNED")
    async def handle_study_problem_assigned(self, payload: StudyProblemAssignedPayload) -> None:
        try:
            data = StudyProblemAssignedSSEResponse.from_payload(payload).model_dump(by_alias=True)
            await self.study_sse_manager.notify(
                study_id=payload.study_id,
                event_type="STUDY_PROBLEM_ASSIGNED",
                payload=data,
                exclude_user_account_id=payload.assigner_user_account_id,
            )
        except Exception as e:
            logger.error(f"[StudyProblemSSEService] STUDY_PROBLEM_ASSIGNED 처리 실패: {e}")
