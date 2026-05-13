from datetime import date, datetime
from sqlalchemy import and_, delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.common.domain.vo.identifiers import ProblemId, StudyId, StudyProblemId, UserAccountId
from app.core.database import Database
from app.study.domain.entity.study_problem import StudyProblem, StudyProblemMember
from app.study.domain.repository.study_problem_repository import StudyProblemRepository
from app.study.infra.mapper.study_problem_mapper import StudyProblemMapper
from app.study.infra.model.study_problem import StudyProblemModel
from app.study.infra.model.study_problem_member import StudyProblemMemberModel


class StudyProblemRepositoryImpl(StudyProblemRepository):
    def __init__(self, db: Database):
        self.db = db

    @property
    def session(self) -> AsyncSession:
        return self.db.get_current_session()

    async def insert(self, study_problem: StudyProblem, members: list[StudyProblemMember]) -> StudyProblem:
        model = StudyProblemMapper.to_model(study_problem)
        self.session.add(model)
        await self.session.flush()

        for member in members:
            member.study_problem_id = StudyProblemId(model.study_problem_id)
            member_model = StudyProblemMapper.member_to_model(member)
            self.session.add(member_model)

        await self.session.flush()
        await self.session.refresh(model, ["members"])
        return StudyProblemMapper.to_entity(model)

    async def insert_members(self, study_problem: StudyProblem, new_members: list[StudyProblemMember]) -> StudyProblem:
        existing_user_ids = {m.user_account_id.value for m in study_problem.members if m.deleted_at is None}

        stmt = (
            select(StudyProblemModel)
            .where(StudyProblemModel.study_problem_id == study_problem.study_problem_id.value)
        )
        result = await self.session.execute(stmt)
        model = result.scalars().one()

        for member in new_members:
            if member.user_account_id.value not in existing_user_ids:
                member.study_problem_id = study_problem.study_problem_id
                member_model = StudyProblemMapper.member_to_model(member)
                self.session.add(member_model)

        await self.session.flush()
        await self.session.refresh(model, ["members"])
        return StudyProblemMapper.to_entity(model)

    async def find_by_study_problem_and_date(
        self, study_id: StudyId, problem_id: ProblemId, target_date: date
    ) -> StudyProblem | None:
        stmt = (
            select(StudyProblemModel)
            .options(selectinload(StudyProblemModel.members))
            .join(
                StudyProblemMemberModel,
                and_(
                    StudyProblemMemberModel.study_problem_id == StudyProblemModel.study_problem_id,
                    StudyProblemMemberModel.deleted_at.is_(None),
                    StudyProblemMemberModel.target_date == target_date,
                ),
            )
            .where(
                and_(
                    StudyProblemModel.study_id == study_id.value,
                    StudyProblemModel.problem_id == problem_id.value,
                    StudyProblemModel.deleted_at.is_(None),
                )
            )
            .limit(1)
        )
        result = await self.session.execute(stmt)
        model = result.scalars().first()
        return StudyProblemMapper.to_entity(model) if model else None

    async def find_by_id(self, study_problem_id: StudyProblemId) -> StudyProblem | None:
        stmt = (
            select(StudyProblemModel)
            .options(selectinload(StudyProblemModel.members))
            .where(
                and_(
                    StudyProblemModel.study_problem_id == study_problem_id.value,
                    StudyProblemModel.deleted_at.is_(None),
                )
            )
        )
        result = await self.session.execute(stmt)
        model = result.scalars().one_or_none()
        return StudyProblemMapper.to_entity(model) if model else None

    async def find_by_study_and_date_range(
        self, study_id: StudyId, start: date, end: date
    ) -> list[StudyProblem]:
        stmt = (
            select(StudyProblemModel)
            .options(selectinload(StudyProblemModel.members))
            .join(
                StudyProblemMemberModel,
                and_(
                    StudyProblemMemberModel.study_problem_id == StudyProblemModel.study_problem_id,
                    StudyProblemMemberModel.deleted_at.is_(None),
                ),
            )
            .where(
                and_(
                    StudyProblemModel.study_id == study_id.value,
                    StudyProblemModel.deleted_at.is_(None),
                    StudyProblemMemberModel.target_date.between(start, end),
                )
            )
            .distinct()
        )
        result = await self.session.execute(stmt)
        models = result.unique().scalars().all()
        return [StudyProblemMapper.to_entity(m) for m in models]

    async def find_by_user_and_date_range(
        self, user_account_id: UserAccountId, start: date, end: date
    ) -> list[StudyProblem]:
        stmt = (
            select(StudyProblemModel)
            .options(selectinload(StudyProblemModel.members))
            .join(
                StudyProblemMemberModel,
                and_(
                    StudyProblemMemberModel.study_problem_id == StudyProblemModel.study_problem_id,
                    StudyProblemMemberModel.user_account_id == user_account_id.value,
                    StudyProblemMemberModel.deleted_at.is_(None),
                    StudyProblemMemberModel.target_date.between(start, end),
                ),
            )
            .where(StudyProblemModel.deleted_at.is_(None))
            .distinct()
        )
        result = await self.session.execute(stmt)
        models = result.unique().scalars().all()
        return [StudyProblemMapper.to_entity(m) for m in models]

    async def soft_delete(self, problem: StudyProblem) -> None:
        problem.deleted_at = datetime.now()
        model = StudyProblemMapper.to_model(problem)
        await self.session.merge(model)
        await self.session.flush()

    async def delete_members_by_user(self, user_account_id: int) -> None:
        stmt = (
            update(StudyProblemMemberModel)
            .where(
                and_(
                    StudyProblemMemberModel.user_account_id == user_account_id,
                    StudyProblemMemberModel.deleted_at.is_(None),
                )
            )
            .values(deleted_at=datetime.now())
        )
        await self.session.execute(stmt)
        await self.session.flush()

    async def delete_members_by_user_hard(self, user_account_id: int) -> None:
        stmt = delete(StudyProblemMemberModel).where(
            StudyProblemMemberModel.user_account_id == user_account_id
        )
        await self.session.execute(stmt)
        await self.session.flush()
