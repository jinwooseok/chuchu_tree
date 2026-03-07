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
        self, user_account_id: UserAccountId
    ) -> list[RecommendationHistory]:
        stmt = (
            select(RecommendationHistoryModel)
            .where(
                and_(
                    RecommendationHistoryModel.requester_user_account_id == user_account_id.value,
                    RecommendationHistoryModel.study_id.is_(None),
                )
            )
            .order_by(RecommendationHistoryModel.created_at.desc())
        )
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [RecommendationHistoryMapper.to_entity(m) for m in models]

    async def find_by_study_id(
        self, study_id: StudyId, user_account_id: UserAccountId | None = None
    ) -> list[RecommendationHistory]:
        conditions = [RecommendationHistoryModel.study_id == study_id.value]
        if user_account_id is not None:
            conditions.append(
                RecommendationHistoryModel.requester_user_account_id == user_account_id.value
            )
        stmt = (
            select(RecommendationHistoryModel)
            .where(and_(*conditions))
            .order_by(RecommendationHistoryModel.created_at.desc())
        )
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [RecommendationHistoryMapper.to_entity(m) for m in models]

    async def delete_by_user_account_id(self, user_account_id: UserAccountId) -> None:
        stmt = delete(RecommendationHistoryModel).where(
            RecommendationHistoryModel.requester_user_account_id == user_account_id.value
        )
        await self.session.execute(stmt)
