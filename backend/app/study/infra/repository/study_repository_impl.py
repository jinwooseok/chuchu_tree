from datetime import datetime
from sqlalchemy import and_, delete, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.baekjoon.infra.model.bj_account import BjAccountModel
from app.common.domain.vo.identifiers import StudyId, UserAccountId
from app.core.database import Database
from app.study.domain.entity.study import Study
from app.study.domain.repository.study_repository import StudyRepository, StudySearchResult
from app.study.infra.mapper.study_mapper import StudyMapper
from app.study.infra.model.study import StudyModel
from app.study.infra.model.study_member import StudyMemberModel
from app.user.infra.model.account_link import AccountLinkModel
from app.user.infra.model.user_account import UserAccountModel


class StudyRepositoryImpl(StudyRepository):
    def __init__(self, db: Database):
        self.db = db

    @property
    def session(self) -> AsyncSession:
        return self.db.get_current_session()

    async def insert(self, study: Study) -> Study:
        model = StudyMapper.to_model(study)
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model, ["members"])
        return StudyMapper.to_entity(model)

    async def find_by_id(self, study_id: StudyId) -> Study | None:
        stmt = (
            select(StudyModel)
            .options(selectinload(StudyModel.members))
            .where(
                and_(
                    StudyModel.study_id == study_id.value,
                    StudyModel.deleted_at.is_(None),
                )
            )
        )
        result = await self.session.execute(stmt)
        model = result.unique().scalars().one_or_none()
        return StudyMapper.to_entity(model) if model else None

    async def find_by_name(self, name: str) -> Study | None:
        stmt = (
            select(StudyModel)
            .options(selectinload(StudyModel.members))
            .where(
                and_(
                    StudyModel.study_name == name,
                    StudyModel.deleted_at.is_(None),
                )
            )
        )
        result = await self.session.execute(stmt)
        model = result.unique().scalars().one_or_none()
        return StudyMapper.to_entity(model) if model else None

    async def search(self, keyword: str, limit: int = 5) -> list[StudySearchResult]:
        stmt = (
            select(
                StudyModel.study_id,
                StudyModel.study_name,
                AccountLinkModel.bj_account_id,
                UserAccountModel.user_code,
                UserAccountModel.profile_image,
                func.count(StudyMemberModel.study_member_id).label("member_count"),
            )
            .join(UserAccountModel, StudyModel.owner_user_account_id == UserAccountModel.user_account_id)
            .join(
                AccountLinkModel,
                and_(
                    AccountLinkModel.user_account_id == StudyModel.owner_user_account_id,
                    AccountLinkModel.deleted_at.is_(None),
                ),
            )
            .outerjoin(
                StudyMemberModel,
                and_(
                    StudyMemberModel.study_id == StudyModel.study_id,
                    StudyMemberModel.deleted_at.is_(None),
                ),
            )
            .where(
                and_(
                    StudyModel.deleted_at.is_(None),
                    or_(
                        StudyModel.study_name.like(f"%{keyword}%"),
                        AccountLinkModel.bj_account_id.like(f"%{keyword}%"),
                        UserAccountModel.user_code.like(f"%{keyword}%"),
                    ),
                )
            )
            .group_by(
                StudyModel.study_id,
                StudyModel.study_name,
                AccountLinkModel.bj_account_id,
                UserAccountModel.user_code,
                UserAccountModel.profile_image,
            )
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        rows = result.all()
        return [
            StudySearchResult(
                study_id=row.study_id,
                study_name=row.study_name,
                owner_bj_account_id=row.bj_account_id,
                owner_user_code=row.user_code,
                member_count=row.member_count,
                owner_profile_image=row.profile_image,
            )
            for row in rows
        ]

    async def find_by_member_user_account_id(self, user_account_id: UserAccountId) -> list[Study]:
        stmt = (
            select(StudyModel)
            .options(selectinload(StudyModel.members))
            .join(
                StudyMemberModel,
                and_(
                    StudyMemberModel.study_id == StudyModel.study_id,
                    StudyMemberModel.user_account_id == user_account_id.value,
                    StudyMemberModel.deleted_at.is_(None),
                ),
            )
            .where(StudyModel.deleted_at.is_(None))
        )
        result = await self.session.execute(stmt)
        models = result.unique().scalars().all()
        return [StudyMapper.to_entity(m) for m in models]

    async def update(self, study: Study) -> Study:
        model = StudyMapper.to_model(study)
        merged = await self.session.merge(model)
        await self.session.flush()
        await self.session.refresh(merged, ["members"])
        return StudyMapper.to_entity(merged)

    async def soft_delete(self, study: Study) -> None:
        study.deleted_at = datetime.now()
        model = StudyMapper.to_model(study)
        await self.session.merge(model)
        await self.session.flush()

    async def is_name_taken(self, name: str) -> bool:
        stmt = select(StudyModel.study_id).where(
            and_(
                StudyModel.study_name == name,
                StudyModel.deleted_at.is_(None),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def delete_members_by_user_hard(self, user_account_id: int) -> None:
        stmt = delete(StudyMemberModel).where(
            StudyMemberModel.user_account_id == user_account_id
        )
        await self.session.execute(stmt)
        await self.session.flush()
