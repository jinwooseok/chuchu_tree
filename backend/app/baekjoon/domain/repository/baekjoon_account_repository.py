from abc import ABC, abstractmethod
from datetime import datetime

from app.baekjoon.domain.entity.baekjoon_account import BaekjoonAccount
from app.baekjoon.domain.vo.tag_account_stat import TagAccountStat
from app.common.domain.vo.identifiers import BaekjoonAccountId, UserAccountId

class BaekjoonAccountRepository(ABC):
    """Repository 인터페이스"""

    @abstractmethod
    async def save(self, account: BaekjoonAccount) -> BaekjoonAccount:
        pass

    @abstractmethod
    async def find_by_id(self, account_id: BaekjoonAccountId) -> BaekjoonAccount|None:
        pass

    @abstractmethod
    async def find_by_user_id(self, user_id: UserAccountId) -> BaekjoonAccount|None:
        pass

    @abstractmethod
    async def find_by_user_id_with_link_date(
        self, user_id: UserAccountId
    ) -> tuple[BaekjoonAccount, datetime] | None:
        """유저 계정 ID로 백준 계정과 연동 일자를 함께 조회"""
        pass

    @abstractmethod
    async def get_tag_stats(self, account_id: BaekjoonAccountId) -> list[TagAccountStat]:
        """백준 계정의 모든 태그별 통계 조회 (영속성 없이 계산)"""
        pass