"""BaekjoonAccount Repository 구현"""

from datetime import date, datetime
from typing import override
from sqlalchemy import and_, func, select, case, null, literal
from sqlalchemy.ext.asyncio import AsyncSession

from app.baekjoon.domain.entity.baekjoon_account import BaekjoonAccount
from app.baekjoon.domain.repository.baekjoon_account_repository import BaekjoonAccountRepository
from app.baekjoon.domain.vo.tag_account_stat import TagAccountStat
from app.baekjoon.infra.mapper.baekjoon_account_mapper import BaekjoonAccountMapper
from app.baekjoon.infra.mapper.problem_history_mapper import ProblemHistoryMapper
from app.baekjoon.infra.model.bj_account import BjAccountModel
from app.baekjoon.infra.model.problem_history import ProblemHistoryModel
from app.common.domain.vo.identifiers import BaekjoonAccountId, TagId, TierId, UserAccountId
from app.core.database import Database
from app.problem.infra.model.problem import ProblemModel
from app.problem.infra.model.problem_tag import ProblemTagModel
from app.user.infra.model.account_link import AccountLinkModel
from app.activity.infra.model.user_problem_status import UserProblemStatusModel
from app.activity.infra.model.problem_date_record import ProblemDateRecordModel, RecordType


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
        model = BaekjoonAccountMapper.to_model(account)
        self.session.add(model)
        await self.session.flush()  # bj_account FK 참조 전에 반드시 flush

        # 문제 히스토리 저장
        for history in account.problem_histories:
            history_model = ProblemHistoryMapper.to_model(history)
            self.session.add(history_model)

    @override
    async def update_stat(self, account: BaekjoonAccount) -> BaekjoonAccount:
        stmt = select(BjAccountModel).where(BjAccountModel.bj_account_id == account.bj_account_id.value)
        result = await self.session.execute(stmt)
        existing_model = result.scalar_one_or_none()

        if existing_model:
            existing_model.tier_id = account.current_tier_id.value
            existing_model.rating = account.rating.value
            existing_model.class_ = account.statistics.class_level
            existing_model.updated_at = datetime.now()
            model = existing_model
        else:
            model = BaekjoonAccountMapper.to_model(account)
            self.session.add(model)

        await self.session.flush()
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
    async def find_all(self) -> list[BaekjoonAccount]:
        """모든 백준 계정 조회"""
        stmt = (
            select(BjAccountModel)
            .where(BjAccountModel.deleted_at.is_(None))
        )

        result = await self.session.execute(stmt)
        models = result.scalars().all()

        return [BaekjoonAccountMapper.to_entity(model) for model in models]

    @override
    async def get_tag_stats(
        self,
        account_id: BaekjoonAccountId,
        user_account_id: UserAccountId | None = None
    ) -> list[TagAccountStat]:
        """백준 계정의 모든 태그별 통계 조회

        streak 제거 후: problem_date_record를 기반으로 last_solved_date 계산
        """
        if user_account_id:
            # user_account_id가 제공되면 problem_date_record로 날짜 조회
            stmt = (
                select(
                    ProblemTagModel.tag_id,
                    func.count(func.distinct(ProblemHistoryModel.problem_id)).label('solved_problem_count'),
                    func.max(ProblemModel.problem_tier_level).label('highest_tier_level'),
                    func.max(ProblemDateRecordModel.marked_date).label('last_solved_date')
                )
                .select_from(ProblemHistoryModel)
                .join(ProblemTagModel, ProblemHistoryModel.problem_id == ProblemTagModel.problem_id)
                .join(ProblemModel, ProblemHistoryModel.problem_id == ProblemModel.problem_id)
                .outerjoin(
                    UserProblemStatusModel,
                    and_(
                        ProblemHistoryModel.problem_id == UserProblemStatusModel.problem_id,
                        UserProblemStatusModel.user_account_id == user_account_id.value,
                        UserProblemStatusModel.solved_yn == True,
                        UserProblemStatusModel.deleted_at.is_(None)
                    )
                )
                .outerjoin(
                    ProblemDateRecordModel,
                    and_(
                        UserProblemStatusModel.user_problem_status_id == ProblemDateRecordModel.user_problem_status_id,
                        ProblemDateRecordModel.record_type == RecordType.SOLVED,
                        ProblemDateRecordModel.deleted_at.is_(None)
                    )
                )
                .where(ProblemHistoryModel.bj_account_id == account_id.value)
                .group_by(ProblemTagModel.tag_id)
            )
        else:
            # user_account_id 없을 때: last_solved_date NULL
            stmt = (
                select(
                    ProblemTagModel.tag_id,
                    func.count(func.distinct(ProblemHistoryModel.problem_id)).label('solved_problem_count'),
                    func.max(ProblemModel.problem_tier_level).label('highest_tier_level'),
                    null().label('last_solved_date')
                )
                .select_from(ProblemHistoryModel)
                .join(ProblemTagModel, ProblemHistoryModel.problem_id == ProblemTagModel.problem_id)
                .join(ProblemModel, ProblemHistoryModel.problem_id == ProblemModel.problem_id)
                .where(ProblemHistoryModel.bj_account_id == account_id.value)
                .group_by(ProblemTagModel.tag_id)
            )

        result = await self.session.execute(stmt)
        rows = result.all()

        stats = []
        for row in rows:
            stats.append(TagAccountStat(
                tag_id=TagId(row.tag_id),
                solved_problem_count=row.solved_problem_count,
                highest_tier_id=TierId(row.highest_tier_level) if row.highest_tier_level else None,
                last_solved_date=row.last_solved_date if row.last_solved_date else None
            ))

        return stats
