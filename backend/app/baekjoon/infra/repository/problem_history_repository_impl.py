"""ProblemHistory Repository 구현"""

from datetime import date
from typing import override

from sqlalchemy import and_, extract, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.activity.domain.entity.problem_date_record import RecordType
from app.activity.infra.model.problem_date_record import ProblemDateRecordModel
from app.activity.infra.model.user_problem_status import UserProblemStatusModel
from app.baekjoon.domain.entity.problem_history import ProblemHistory
from app.baekjoon.domain.repository.problem_history_repository import ProblemHistoryRepository
from app.baekjoon.infra.mapper.problem_history_mapper import ProblemHistoryMapper
from app.baekjoon.infra.model.problem_history import ProblemHistoryModel
from app.common.domain.vo.identifiers import BaekjoonAccountId, UserAccountId
from app.core.database import Database
from app.user.infra.model.account_link import AccountLinkModel


class ProblemHistoryRepositoryImpl(ProblemHistoryRepository):
    """문제 풀이 기록 Repository 구현체"""

    def __init__(self, db: Database):
        self.db = db

    @property
    def session(self) -> AsyncSession:
        return self.db.get_current_session()

    @override
    async def find_by_account_id(
        self,
        bj_account_id: BaekjoonAccountId
    ) -> list[ProblemHistory]:
        """백준 계정 ID로 모든 문제 풀이 기록 조회"""
        stmt = (
            select(ProblemHistoryModel)
            .where(ProblemHistoryModel.bj_account_id == bj_account_id.value)
            .order_by(ProblemHistoryModel.created_at.asc())
        )

        result = await self.session.execute(stmt)
        models = result.scalars().all()

        return [ProblemHistoryMapper.to_entity(model) for model in models]

    @override
    async def find_by_account_and_date_range(
        self,
        bj_account_id: BaekjoonAccountId,
        start_date: date,
        end_date: date
    ) -> list[ProblemHistory]:
        """백준 계정 ID와 날짜 범위로 문제 풀이 기록 조회"""
        stmt = (
            select(ProblemHistoryModel)
            .where(
                and_(
                    ProblemHistoryModel.bj_account_id == bj_account_id.value,
                    func.date(ProblemHistoryModel.created_at) >= start_date,
                    func.date(ProblemHistoryModel.created_at) <= end_date
                )
            )
            .order_by(ProblemHistoryModel.created_at.asc())
        )

        result = await self.session.execute(stmt)
        models = result.scalars().all()

        return [ProblemHistoryMapper.to_entity(model) for model in models]

    @override
    async def find_by_account_and_month(
        self,
        bj_account_id: BaekjoonAccountId,
        year: int,
        month: int
    ) -> dict[int, date]:
        """
        streak 제거 후 빈 dict 반환 (호환성 유지)
        월간 문제 날짜는 이제 problem_date_record를 통해 activity 도메인에서 처리됩니다.
        """
        return {}

    @override
    async def find_solved_ids_in_list(
        self,
        bj_account_id: BaekjoonAccountId,
        problem_ids: list[int]
    ) -> set[int]:
        """주어진 문제 목록 중 유저가 한 번이라도 푼 적 있는 ID들만 조회"""
        if not problem_ids:
            return set()

        stmt = (
            select(ProblemHistoryModel.problem_id)
            .where(
                and_(
                    ProblemHistoryModel.bj_account_id == bj_account_id.value,
                    ProblemHistoryModel.problem_id.in_(problem_ids)
                )
            )
        )

        result = await self.session.execute(stmt)
        return set(result.scalars().all())

    @override
    async def find_solved_ids_by_bj_account_id(
        self,
        bj_account_id: BaekjoonAccountId
    ) -> set[int]:
        """유저가 한 번이라도 푼 적 있는 ID들만 조회"""
        stmt = (
            select(ProblemHistoryModel.problem_id)
            .where(ProblemHistoryModel.bj_account_id == bj_account_id.value)
        )

        result = await self.session.execute(stmt)
        return set(result.scalars().all())

    @override
    async def save_all(
        self,
        problem_histories: list[ProblemHistory]
    ) -> None:
        models = [ProblemHistoryMapper.to_model(ph) for ph in problem_histories]
        self.session.add_all(models)
        await self.session.flush()

    @override
    async def find_by_problem_ids(
        self,
        bj_account_id: BaekjoonAccountId,
        problem_ids: list[int]
    ) -> list[ProblemHistory]:
        """특정 문제 ID들의 problem_history 조회 (streak 없이)"""
        if not problem_ids:
            return []

        stmt = (
            select(ProblemHistoryModel)
            .where(
                and_(
                    ProblemHistoryModel.bj_account_id == bj_account_id.value,
                    ProblemHistoryModel.problem_id.in_(problem_ids)
                )
            )
        )

        result = await self.session.execute(stmt)
        models = result.scalars().all()

        return [ProblemHistoryMapper.to_entity(model) for model in models]

    @override
    async def find_unrecorded_problem_ids(
        self,
        user_account_id: UserAccountId,
        bj_account_id: BaekjoonAccountId
    ) -> set[int]:
        """problem_history에는 있지만 활성 SOLVED date_record가 없는 문제 ID 조회.

        링크 시 user_problem_status는 생성되지만 problem_date_record는 생성되지 않으므로,
        user_problem_status 존재 여부가 아닌 problem_date_record(SOLVED) 존재 여부로 판단.
        """
        # ① 활성 SOLVED date_record가 있는 problem_id (진짜 기록됨)
        recorded_subq = (
            select(UserProblemStatusModel.problem_id)
            .join(
                ProblemDateRecordModel,
                and_(
                    UserProblemStatusModel.user_problem_status_id == ProblemDateRecordModel.user_problem_status_id,
                    ProblemDateRecordModel.record_type == RecordType.SOLVED,
                    ProblemDateRecordModel.deleted_at.is_(None)
                )
            )
            .where(
                and_(
                    UserProblemStatusModel.user_account_id == user_account_id.value,
                    UserProblemStatusModel.banned_yn == False,
                    UserProblemStatusModel.deleted_at.is_(None)
                )
            )
        ).scalar_subquery()

        # ② 유저가 밴한 problem_id (제외 대상)
        banned_subq = (
            select(UserProblemStatusModel.problem_id)
            .where(
                and_(
                    UserProblemStatusModel.user_account_id == user_account_id.value,
                    UserProblemStatusModel.banned_yn == True,
                    UserProblemStatusModel.deleted_at.is_(None)
                )
            )
        ).scalar_subquery()

        # 미기록 = problem_history에 있으나 기록됨/밴 제외
        stmt = (
            select(ProblemHistoryModel.problem_id)
            .where(
                and_(
                    ProblemHistoryModel.bj_account_id == bj_account_id.value,
                    ProblemHistoryModel.problem_id.not_in(recorded_subq),
                    ProblemHistoryModel.problem_id.not_in(banned_subq)
                )
            )
        )

        result = await self.session.execute(stmt)
        return set(result.scalars().all())

    # ─── Deprecated method stubs for backward compatibility ─────────────────

    async def find_by_account_and_month_with_streak(
        self,
        bj_account_id: BaekjoonAccountId,
        year: int,
        month: int
    ) -> dict[int, date]:
        """Deprecated: streak 제거 후 빈 dict 반환"""
        return {}

    async def find_by_problem_ids_with_streak(
        self,
        bj_account_id: BaekjoonAccountId,
        problem_ids: list[int]
    ) -> list[ProblemHistory]:
        """Deprecated: streak 없이 problem_history만 조회"""
        return await self.find_by_problem_ids(bj_account_id, problem_ids)
