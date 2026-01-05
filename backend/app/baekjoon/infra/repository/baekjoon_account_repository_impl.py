"""BaekjoonAccount Repository 구현"""

from datetime import datetime
from typing import override
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.baekjoon.domain.entity.baekjoon_account import BaekjoonAccount
from app.baekjoon.domain.repository.baekjoon_account_repository import BaekjoonAccountRepository
from app.baekjoon.domain.vo.tag_account_stat import TagAccountStat
from app.baekjoon.infra.mapper.baekjoon_account_mapper import BaekjoonAccountMapper
from app.baekjoon.infra.mapper.problem_history_mapper import ProblemHistoryMapper
from app.baekjoon.infra.mapper.streak_mapper import StreakMapper
from app.baekjoon.infra.model.bj_account import BjAccountModel
from app.baekjoon.infra.model.problem_history import ProblemHistoryModel
from app.common.domain.vo.identifiers import BaekjoonAccountId, TagId, TierId, UserAccountId
from app.core.database import Database
from app.problem.infra.model.problem import ProblemModel
from app.problem.infra.model.problem_tag import ProblemTagModel
from app.user.infra.model.account_link import AccountLinkModel


class BaekjoonAccountRepositoryImpl(BaekjoonAccountRepository):
    """백준 계정 Repository 구현체"""

    def __init__(self, db: Database):
        self.db = db

    @property
    def session(self) -> AsyncSession:
        return self.db.get_current_session()

    @override
    async def save(self, account: BaekjoonAccount) -> BaekjoonAccount:
        """백준 계정 저장"""
        # 백준 계정 모델로 변환
        model = BaekjoonAccountMapper.to_model(account)
        self.session.add(model)

        # 문제 히스토리 저장
        for history in account.problem_histories:
            history_model = ProblemHistoryMapper.to_model(history)
            self.session.add(history_model)

        # 스트릭 저장
        for streak in account.streaks:
            streak_model = StreakMapper.to_model(streak)
            self.session.add(streak_model)

        await self.session.flush()  # ID 생성을 위해 flush

        return BaekjoonAccountMapper.to_entity(model)

    @override
    async def find_by_id(self, account_id: BaekjoonAccountId) -> BaekjoonAccount | None:
        """백준 계정 ID로 조회"""
        stmt = select(BjAccountModel).where(
            and_(
                BjAccountModel.bj_account_id == account_id.value,
                BjAccountModel.deleted_at.is_(None)
            )
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()

        return BaekjoonAccountMapper.to_entity(model) if model else None

    @override
    async def find_by_user_id(self, user_id: UserAccountId) -> BaekjoonAccount | None:
        """유저 계정 ID로 백준 계정 조회 (AccountLink를 통해)"""
        # AccountLink를 조인하여 백준 계정 조회
        stmt = (
            select(BjAccountModel)
            .join(
                AccountLinkModel,
                BjAccountModel.bj_account_id == AccountLinkModel.bj_account_id
            )
            .where(
                and_(
                    AccountLinkModel.user_account_id == user_id.value,
                    AccountLinkModel.deleted_at.is_(None),
                    BjAccountModel.deleted_at.is_(None)
                )
            )
        )

        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()

        return BaekjoonAccountMapper.to_entity(model) if model else None

    @override
    async def find_by_user_id_with_link_date(
        self, user_id: UserAccountId
    ) -> tuple[BaekjoonAccount, datetime] | None:
        """유저 계정 ID로 백준 계정과 연동 일자를 함께 조회"""
        # AccountLink와 BjAccount를 조인하여 함께 조회
        stmt = (
            select(BjAccountModel, AccountLinkModel.created_at)
            .join(
                AccountLinkModel,
                BjAccountModel.bj_account_id == AccountLinkModel.bj_account_id
            )
            .where(
                and_(
                    AccountLinkModel.user_account_id == user_id.value,
                    AccountLinkModel.deleted_at.is_(None),
                    BjAccountModel.deleted_at.is_(None)
                )
            )
        )

        result = await self.session.execute(stmt)
        row = result.one_or_none()

        if not row:
            return None

        bj_account_model, linked_at = row
        bj_account = BaekjoonAccountMapper.to_entity(bj_account_model)

        return (bj_account, linked_at)

    @override
    async def get_tag_stats(self, account_id: BaekjoonAccountId) -> list[TagAccountStat]:
        """백준 계정의 모든 태그별 통계 조회 (영속성 없이 계산)"""
        # 태그별로 풀이 통계 집계
        stmt = (
            select(
                ProblemTagModel.tag_id,
                func.count(func.distinct(ProblemHistoryModel.problem_id)).label('solved_problem_count'),
                func.max(ProblemModel.problem_tier_level).label('highest_tier_level'),
                func.max(ProblemHistoryModel.created_at).label('last_solved_date')
            )
            .select_from(ProblemHistoryModel)
            .join(ProblemTagModel, ProblemHistoryModel.problem_id == ProblemTagModel.problem_id)
            .join(ProblemModel, ProblemHistoryModel.problem_id == ProblemModel.problem_id)
            .where(ProblemHistoryModel.bj_account_id == account_id.value)
            .group_by(ProblemTagModel.tag_id)
        )

        result = await self.session.execute(stmt)
        rows = result.all()

        # VO 리스트로 변환
        stats = []
        for row in rows:
            stats.append(TagAccountStat(
                tag_id=TagId(row.tag_id),
                solved_problem_count=row.solved_problem_count,
                highest_tier_id=TierId(row.highest_tier_level) if row.highest_tier_level else None,
                last_solved_date=row.last_solved_date.date() if row.last_solved_date else None
            ))

        return stats
