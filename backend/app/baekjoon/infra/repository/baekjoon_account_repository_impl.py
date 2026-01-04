"""BaekjoonAccount Repository 구현"""

from typing import override
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.baekjoon.domain.entity.baekjoon_account import BaekjoonAccount
from app.baekjoon.domain.repository.baekjoon_account_repository import BaekjoonAccountRepository
from app.baekjoon.infra.mapper.baekjoon_account_mapper import BaekjoonAccountMapper
from app.baekjoon.infra.mapper.problem_history_mapper import ProblemHistoryMapper
from app.baekjoon.infra.mapper.streak_mapper import StreakMapper
from app.baekjoon.infra.model.bj_account import BjAccountModel
from app.baekjoon.infra.model.problem_history import ProblemHistoryModel
from app.baekjoon.infra.model.streak import StreakModel
from app.common.domain.vo.identifiers import BaekjoonAccountId, UserAccountId
from app.core.database import Database


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
        # TODO: AccountLink 테이블을 조인하여 조회하는 로직 구현
        # 현재는 간단히 None 반환
        return None
