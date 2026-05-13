from app.common.domain.vo.identifiers import StudyId, UserAccountId
from app.core.database import transactional
from app.recommendation.application.command.recommendation_history_command import (
    SaveRecommendationHistoryCommand,
)
from app.recommendation.domain.entity.recommendation_history import RecommendationHistory
from app.recommendation.domain.repository.recommendation_history_repository import (
    RecommendationHistoryRepository,
)


class SaveRecommendationHistoryUsecase:

    def __init__(self, recommendation_history_repository: RecommendationHistoryRepository):
        self.recommendation_history_repository = recommendation_history_repository

    @transactional
    async def execute(self, command: SaveRecommendationHistoryCommand) -> None:
        history = RecommendationHistory.create(
            requester_user_account_id=UserAccountId(command.requester_user_account_id),
            study_id=StudyId(command.study_id) if command.study_id is not None else None,
            params=command.params,
            recommended_problem_ids=command.recommended_problem_ids,
        )
        await self.recommendation_history_repository.save(history)
