"""UserDateRecord Repository 인터페이스"""

from abc import ABC, abstractmethod
from datetime import date

from app.activity.domain.entity.user_date_record import UserDateRecord
from app.common.domain.vo.identifiers import UserAccountId


class UserDateRecordRepository(ABC):
    """유저 날짜별 풀이 수 Repository 인터페이스"""

    @abstractmethod
    async def find_by_user_and_date_range(
        self,
        user_account_id: UserAccountId,
        bj_account_id: str,
        start_date: date,
        end_date: date
    ) -> list[UserDateRecord]:
        """유저 ID + BJ 계정 + 날짜 범위로 기록 조회"""
        pass

    @abstractmethod
    async def find_by_user_and_date(
        self,
        user_account_id: UserAccountId,
        bj_account_id: str,
        target_date: date
    ) -> UserDateRecord | None:
        """유저 ID + BJ 계정 + 날짜로 단일 기록 조회"""
        pass

    @abstractmethod
    async def upsert(self, record: UserDateRecord) -> UserDateRecord:
        """날짜별 기록 저장 또는 업데이트 (UPSERT)"""
        pass

    @abstractmethod
    async def upsert_increment(
        self,
        user_account_id: UserAccountId,
        bj_account_id: str,
        target_date: date,
        increment: int
    ) -> UserDateRecord:
        """solved_count 증가 방식으로 UPSERT

        해당 날짜 기록이 없으면 생성, 있으면 solved_count += increment
        """
        pass

    @abstractmethod
    async def save_all(self, records: list[UserDateRecord]) -> None:
        """여러 기록 일괄 저장 (신규만, 중복 skip)"""
        pass
