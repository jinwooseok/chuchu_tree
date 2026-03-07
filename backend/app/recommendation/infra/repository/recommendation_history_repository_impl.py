from sqlalchemy import and_, delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.domain.vo.identifiers import StudyId, UserAccountId
from app.core.database import Database
from app.recommendation.domain.entity.recommendation_history import RecommendationHistory
from app.recommendation.domain.repository.recommendation_history_repository import (
    RecommendationHistoryRepository,
)
from app.recommendation.infra.mapper.recommendation_history_mapper import RecommendationHistoryMapper
from app.recommendation.infra.model.recommendation_history import RecommendationHistoryModel


class RecommendationHistoryRepositoryImpl(RecommendationHistoryRepository):

    def __init__(self, db: Database):
        self.db = db

    @property
    def session(self) -> AsyncSession:
        return self.db.get_current_session()

    async def save(self, history: RecommendationHistory) -> RecommendationHistory:
        model = RecommendationHistoryMapper.to_model(history)
        self.session.add(model)
        await self.session.flush()
        return RecommendationHistoryMapper.to_entity(model)

    async def find_by_user_account_id(
        self, user_account_id: UserAccountId, cursor: int | None = None, limit: int = 10
    ) -> list[RecommendationHistory]:
        conditions = [
            RecommendationHistoryModel.requester_user_account_id == user_account_id.value,
            RecommendationHistoryModel.study_id.is_(None),
        ]
        if cursor is not None:
            conditions.append(RecommendationHistoryModel.recommendation_history_id < cursor)
        stmt = (
            select(RecommendationHistoryModel)
            .where(and_(*conditions))
            .order_by(RecommendationHistoryModel.recommendation_history_id.desc())
            .limit(limit + 1)
        )
        result = await self.session.execute(stmt)
        return [RecommendationHistoryMapper.to_entity(m) for m in result.scalars().all()]

    async def find_by_study_id(
        self,
        study_id: StudyId,
        user_account_id: UserAccountId | None = None,
        cursor: int | None = None,
        limit: int = 10,
    ) -> list[RecommendationHistory]:
        conditions = [RecommendationHistoryModel.study_id == study_id.value]
        if user_account_id is not None:
            conditions.append(
                RecommendationHistoryModel.requester_user_account_id == user_account_id.value
            )
        if cursor is not None:
            conditions.append(RecommendationHistoryModel.recommendation_history_id < cursor)
        stmt = (
            select(RecommendationHistoryModel)
            .where(and_(*conditions))
            .order_by(RecommendationHistoryModel.recommendation_history_id.desc())
            .limit(limit + 1)
        )
        result = await self.session.execute(stmt)
        return [RecommendationHistoryMapper.to_entity(m) for m in result.scalars().all()]

    async def delete_by_user_account_id(self, user_account_id: UserAccountId) -> None:
        stmt = delete(RecommendationHistoryModel).where(
            RecommendationHistoryModel.requester_user_account_id == user_account_id.value
        )
        await self.session.execute(stmt)
