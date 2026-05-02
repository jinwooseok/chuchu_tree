from datetime import datetime
from sqlalchemy import and_, delete, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.domain.enums import InvitationStatus
from app.common.domain.vo.identifiers import StudyId, StudyInvitationId, UserAccountId
from app.core.database import Database
from app.study.domain.entity.study_invitation import StudyInvitation
from app.study.domain.repository.study_invitation_repository import StudyInvitationRepository
from app.study.infra.mapper.study_invitation_mapper import StudyInvitationMapper
from app.study.infra.model.study_invitation import StudyInvitationModel


class StudyInvitationRepositoryImpl(StudyInvitationRepository):
    def __init__(self, db: Database):
        self.db = db

    @property
    def session(self) -> AsyncSession:
        return self.db.get_current_session()

    async def insert(self, invitation: StudyInvitation) -> StudyInvitation:
        model = StudyInvitationMapper.to_model(invitation)
        self.session.add(model)
        await self.session.flush()
        return StudyInvitationMapper.to_entity(model)

    async def find_by_id(self, invitation_id: StudyInvitationId) -> StudyInvitation | None:
        stmt = select(StudyInvitationModel).where(
            StudyInvitationModel.invitation_id == invitation_id.value
        )
        result = await self.session.execute(stmt)
        model = result.scalars().one_or_none()
        return StudyInvitationMapper.to_entity(model) if model else None

    async def find_pending_by_invitee(self, invitee_id: UserAccountId) -> list[StudyInvitation]:
        stmt = select(StudyInvitationModel).where(
            and_(
                StudyInvitationModel.invitee_user_account_id == invitee_id.value,
                StudyInvitationModel.status == InvitationStatus.PENDING,
                StudyInvitationModel.deleted_at.is_(None),
            )
        )
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [StudyInvitationMapper.to_entity(m) for m in models]

    async def find_by_invitee(self, invitee_id: UserAccountId) -> list[StudyInvitation]:
        stmt = select(StudyInvitationModel).where(
            and_(
                StudyInvitationModel.invitee_user_account_id == invitee_id.value,
                StudyInvitationModel.deleted_at.is_(None),
            )
        )
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [StudyInvitationMapper.to_entity(m) for m in models]

    async def find_by_study_and_invitee(
        self, study_id: StudyId, invitee_id: UserAccountId
    ) -> StudyInvitation | None:
        stmt = select(StudyInvitationModel).where(
            and_(
                StudyInvitationModel.study_id == study_id.value,
                StudyInvitationModel.invitee_user_account_id == invitee_id.value,
                StudyInvitationModel.status == InvitationStatus.PENDING,
                StudyInvitationModel.deleted_at.is_(None),
            )
        )
        result = await self.session.execute(stmt)
        model = result.scalars().one_or_none()
        return StudyInvitationMapper.to_entity(model) if model else None

    async def find_pending_by_study(self, study_id: StudyId) -> list[StudyInvitation]:
        stmt = select(StudyInvitationModel).where(
            and_(
                StudyInvitationModel.study_id == study_id.value,
                StudyInvitationModel.status == InvitationStatus.PENDING,
                StudyInvitationModel.deleted_at.is_(None),
            )
        )
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [StudyInvitationMapper.to_entity(m) for m in models]

    async def update(self, invitation: StudyInvitation) -> StudyInvitation:
        model = StudyInvitationMapper.to_model(invitation)
        merged = await self.session.merge(model)
        await self.session.flush()
        return StudyInvitationMapper.to_entity(merged)

    async def soft_delete(self, invitation: StudyInvitation) -> None:
        invitation.deleted_at = datetime.now()
        model = StudyInvitationMapper.to_model(invitation)
        await self.session.merge(model)
        await self.session.flush()

    async def delete_all_by_user_account_id(self, user_account_id: UserAccountId) -> None:
        stmt = delete(StudyInvitationModel).where(
            or_(
                StudyInvitationModel.invitee_user_account_id == user_account_id.value,
                StudyInvitationModel.inviter_user_account_id == user_account_id.value,
            )
        )
        await self.session.execute(stmt)
        await self.session.flush()

    async def soft_delete_all_by_study_id(self, study_id: StudyId) -> None:
        stmt = (
            update(StudyInvitationModel)
            .where(
                and_(
                    StudyInvitationModel.study_id == study_id.value,
                    StudyInvitationModel.deleted_at.is_(None),
                )
            )
            .values(deleted_at=datetime.now())
        )
        await self.session.execute(stmt)
        await self.session.flush()
