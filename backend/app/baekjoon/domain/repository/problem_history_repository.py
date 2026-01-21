"""ProblemHistory Repository 인터페이스"""

from abc import ABC, abstractmethod
from datetime import date

from app.baekjoon.domain.entity.problem_history import ProblemHistory
from app.common.domain.vo.identifiers import BaekjoonAccountId, UserAccountId


class ProblemHistoryRepository(ABC):
    """문제 풀이 기록 Repository 인터페이스"""
    
    @abstractmethod
    async def save_all(
        self,
        problem_histories: list[ProblemHistory]
    ) -> None:
        pass
    
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
    async def find_solved_ids_in_list(
        self,
        bj_account_id: BaekjoonAccountId,
        problem_ids: list[int]
    ) -> set[int]:
        """
        백준 계정 ID와 날짜 범위로 문제 풀이 기록 조회

        Args:
            bj_account_id: 백준 계정 ID

        Returns:
            문제 풀이 기록 목록 (날짜 오름차순)
        """
        pass
    
    @abstractmethod
    async def find_solved_ids_by_bj_account_id(
        self,
        bj_account_id: BaekjoonAccountId
    ) -> set[int]:
        """
        백준 계정 ID와 날짜 범위로 문제 풀이 기록 조회

        Args:
            bj_account_id: 백준 계정 ID

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

    @abstractmethod
    async def find_by_problem_ids_with_streak(
        self,
        bj_account_id: BaekjoonAccountId,
        problem_ids: list[int]
    ) -> list[ProblemHistory]:
        """
        특정 문제 ID들의 problem_history를 streak과 함께 조회

        Args:
            bj_account_id: 백준 계정 ID
            problem_ids: 조회할 문제 ID 목록

        Returns:
            ProblemHistory 엔티티 목록 (streak_date 포함)
        """
        pass

    @abstractmethod
    async def find_unrecorded_problem_ids(
        self,
        user_account_id: UserAccountId,
        bj_account_id: BaekjoonAccountId
    ) -> set[int]:
        """
        problem_history에는 있지만 problem_record에 기록되지 않은 문제 ID 조회

        problem_history와 problem_record를 조인하여,
        solved.ac에서는 풀었지만 우리 시스템에 기록되지 않은 문제들을 찾습니다.

        bj_account와 user_account는 다대다 관계이므로 둘 다 체크합니다.

        Args:
            user_account_id: 유저 계정 ID (VO)
            bj_account_id: 백준 계정 ID (VO)

        Returns:
            기록되지 않은 문제 ID 집합
        """
        pass
