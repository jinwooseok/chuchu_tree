from datetime import datetime
from sqlalchemy import and_, delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.domain.enums import ApplicationStatus
from app.common.domain.vo.identifiers import StudyApplicationId, StudyId, UserAccountId
from app.core.database import Database
from app.study.domain.entity.study_application import StudyApplication
from app.study.domain.repository.study_application_repository import StudyApplicationRepository
from app.study.infra.mapper.study_application_mapper import StudyApplicationMapper
from app.study.infra.model.study_application import StudyApplicationModel


class StudyApplicationRepositoryImpl(StudyApplicationRepository):
    def __init__(self, db: Database):
        self.db = db

    @property
    def session(self) -> AsyncSession:
        return self.db.get_current_session()

    async def insert(self, application: StudyApplication) -> StudyApplication:
        model = StudyApplicationMapper.to_model(application)
        self.session.add(model)
        await self.session.flush()
        return StudyApplicationMapper.to_entity(model)

    async def find_by_id(self, application_id: StudyApplicationId) -> StudyApplication | None:
        stmt = select(StudyApplicationModel).where(
            StudyApplicationModel.application_id == application_id.value
        )
        result = await self.session.execute(stmt)
        model = result.scalars().one_or_none()
        return StudyApplicationMapper.to_entity(model) if model else None

    async def find_pending_by_study(self, study_id: StudyId) -> list[StudyApplication]:
        stmt = select(StudyApplicationModel).where(
            and_(
                StudyApplicationModel.study_id == study_id.value,
                StudyApplicationModel.status == ApplicationStatus.PENDING,
                StudyApplicationModel.deleted_at.is_(None),
            )
        )
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [StudyApplicationMapper.to_entity(m) for m in models]

    async def find_pending_by_applicant(self, applicant_id: UserAccountId) -> list[StudyApplication]:
        stmt = select(StudyApplicationModel).where(
            and_(
                StudyApplicationModel.applicant_user_account_id == applicant_id.value,
                StudyApplicationModel.status == ApplicationStatus.PENDING,
                StudyApplicationModel.deleted_at.is_(None),
            )
        )
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [StudyApplicationMapper.to_entity(m) for m in models]

    async def find_by_study_and_applicant(
        self, study_id: StudyId, applicant_id: UserAccountId
    ) -> StudyApplication | None:
        stmt = select(StudyApplicationModel).where(
            and_(
                StudyApplicationModel.study_id == study_id.value,
                StudyApplicationModel.applicant_user_account_id == applicant_id.value,
                StudyApplicationModel.status == ApplicationStatus.PENDING,
                StudyApplicationModel.deleted_at.is_(None),
            )
        )
        result = await self.session.execute(stmt)
        model = result.scalars().one_or_none()
        return StudyApplicationMapper.to_entity(model) if model else None

    async def update(self, application: StudyApplication) -> StudyApplication:
        model = StudyApplicationMapper.to_model(application)
        merged = await self.session.merge(model)
        await self.session.flush()
        return StudyApplicationMapper.to_entity(merged)

    async def soft_delete(self, application: StudyApplication) -> None:
        application.deleted_at = datetime.now()
        model = StudyApplicationMapper.to_model(application)
        await self.session.merge(model)
        await self.session.flush()

    async def delete_all_by_user_account_id(self, user_account_id: UserAccountId) -> None:
        stmt = delete(StudyApplicationModel).where(
            StudyApplicationModel.applicant_user_account_id == user_account_id.value
        )
        await self.session.execute(stmt)
        await self.session.flush()

    async def soft_delete_all_by_study_id(self, study_id: StudyId) -> None:
        stmt = (
            update(StudyApplicationModel)
            .where(
                and_(
                    StudyApplicationModel.study_id == study_id.value,
                    StudyApplicationModel.deleted_at.is_(None),
                )
            )
            .values(deleted_at=datetime.now())
        )
        await self.session.execute(stmt)
        await self.session.flush()
