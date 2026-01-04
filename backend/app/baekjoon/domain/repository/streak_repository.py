"""Streak Repository 인터페이스"""

from abc import ABC, abstractmethod
from datetime import date

from app.baekjoon.domain.entity.streak import Streak
from app.common.domain.vo.identifiers import BaekjoonAccountId


class StreakRepository(ABC):
    """스트릭 Repository 인터페이스"""

    @abstractmethod
    async def find_by_account_and_date_range(
        self,
        bj_account_id: BaekjoonAccountId,
        start_date: date,
        end_date: date
    ) -> list[Streak]:
        """
        백준 계정 ID와 날짜 범위로 스트릭 조회

        Args:
            bj_account_id: 백준 계정 ID
            start_date: 시작 날짜
            end_date: 종료 날짜

        Returns:
            스트릭 목록 (날짜 오름차순)
        """
        pass