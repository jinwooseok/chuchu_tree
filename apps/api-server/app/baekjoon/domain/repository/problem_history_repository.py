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
        """백준 계정 ID로 모든 문제 풀이 기록 조회"""
        pass

    @abstractmethod
    async def find_by_account_and_date_range(
        self,
        bj_account_id: BaekjoonAccountId,
        start_date: date,
        end_date: date
    ) -> list[ProblemHistory]:
        """백준 계정 ID와 날짜 범위로 문제 풀이 기록 조회"""
        pass

    @abstractmethod
    async def find_solved_ids_in_list(
        self,
        bj_account_id: BaekjoonAccountId,
        problem_ids: list[int]
    ) -> set[int]:
        """주어진 문제 목록 중 유저가 한 번이라도 푼 적 있는 ID들만 조회"""
        pass

    @abstractmethod
    async def find_solved_ids_by_bj_account_id(
        self,
        bj_account_id: BaekjoonAccountId
    ) -> set[int]:
        """유저가 한 번이라도 푼 적 있는 ID들만 조회"""
        pass

    @abstractmethod
    async def find_by_account_and_month(
        self,
        bj_account_id: BaekjoonAccountId,
        year: int,
        month: int
    ) -> dict[int, date]:
        """
        백준 계정 ID와 년/월로 문제 풀이 기록 조회
        streak 제거 후 항상 빈 dict 반환 (호환성 유지)

        Returns:
            {} (빈 딕셔너리 - streak 기반 날짜 매핑 더 이상 사용 안 함)
        """
        pass

    @abstractmethod
    async def find_by_problem_ids(
        self,
        bj_account_id: BaekjoonAccountId,
        problem_ids: list[int]
    ) -> list[ProblemHistory]:
        """특정 문제 ID들의 problem_history 조회"""
        pass

    @abstractmethod
    async def find_unrecorded_problem_ids(
        self,
        user_account_id: UserAccountId,
        bj_account_id: BaekjoonAccountId
    ) -> set[int]:
        """
        problem_history에는 있지만 user_problem_status에 기록되지 않은 문제 ID 조회
        """
        pass
