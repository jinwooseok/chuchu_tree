"""ProblemHistory Repository 인터페이스"""

from abc import ABC, abstractmethod
from datetime import date

from app.baekjoon.domain.entity.problem_history import ProblemHistory
from app.common.domain.vo.identifiers import BaekjoonAccountId


class ProblemHistoryRepository(ABC):
    """문제 풀이 기록 Repository 인터페이스"""

    @abstractmethod
    async def find_by_account_id(
        self,
        bj_account_id: BaekjoonAccountId
    ) -> list[ProblemHistory]:
        """
        백준 계정 ID로 모든 문제 풀이 기록 조회

        Args:
            bj_account_id: 백준 계정 ID

        Returns:
            문제 풀이 기록 목록 (날짜 오름차순)
        """
        pass

    @abstractmethod
    async def find_by_account_and_date_range(
        self,
        bj_account_id: BaekjoonAccountId,
        start_date: date,
        end_date: date
    ) -> list[ProblemHistory]:
        """
        백준 계정 ID와 날짜 범위로 문제 풀이 기록 조회

        Args:
            bj_account_id: 백준 계정 ID
            start_date: 시작 날짜
            end_date: 종료 날짜

        Returns:
            문제 풀이 기록 목록 (날짜 오름차순)
        """
        pass

    @abstractmethod
    async def find_by_account_and_month_with_streak(
        self,
        bj_account_id: BaekjoonAccountId,
        year: int,
        month: int
    ) -> dict[int, date]:
        """
        백준 계정 ID와 년/월로 Streak과 연동된 문제 풀이 기록 조회
        (streak_id가 NOT NULL인 것만, Streak의 날짜 기준)

        Args:
            bj_account_id: 백준 계정 ID
            year: 년도
            month: 월

        Returns:
            {problem_id: streak_date} 딕셔너리
        """
        pass
