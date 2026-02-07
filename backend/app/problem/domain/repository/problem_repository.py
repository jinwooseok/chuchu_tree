from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from app.common.domain.vo.identifiers import ProblemId, TagId
from app.common.domain.vo.primitives import TierRange
from app.problem.domain.entity.problem import Problem, TierLevel

if TYPE_CHECKING:
    from app.recommendation.domain.vo.search_criteria import SearchCriteria

class ProblemRepository(ABC):
    """Repository 인터페이스"""

    @abstractmethod
    async def save(self, problem: Problem) -> Problem:
        pass

    @abstractmethod
    async def find_by_id(self, problem_id: ProblemId) -> Problem|None:
        pass

    @abstractmethod
    async def find_by_ids(self, problem_ids: list[ProblemId]) -> list[Problem]:
        """여러 문제 ID로 조회 (태그 포함)"""
        pass

    @abstractmethod
    async def find_by_tier_range(
        self,
        min_tier: TierLevel,
        max_tier: TierLevel
    ) -> list[Problem]:
        pass

    @abstractmethod
    async def find_by_tags(self, tag_ids: list[TagId]) -> list[Problem]:
        pass
    
    @abstractmethod
    async def find_by_id_prefix(self, prefix: str, limit: int = 5) -> list[Problem]:
        """문제 ID가 특정 문자열로 시작하는 문제들을 조회"""
        pass

    @abstractmethod
    async def find_by_title_keyword(self, keyword: str, limit: int = 5) -> list[Problem]:
        """문제 제목에 키워드가 포함된 문제들을 조회"""
        pass

    @abstractmethod
    async def find_recommended_problem(
        self,
        tag_id: TagId,
        criteria_list: list['SearchCriteria'],
        min_solved_count: int,
        exclude_ids: set[int],
        priority_ids: set[int]
    ) -> Problem | None:
        """추천 문제 조회

        Args:
            tag_id: 태그 ID
            criteria_list: 검색 조건 리스트 (각 레벨 필터별 독립적인 tier_range + skill_rate)
            min_solved_count: 최소 해결 수 (1000명 이상 푼 문제)
            exclude_ids: 제외할 문제 ID 집합 (이미 푼 문제 + ban한 문제)
            priority_ids: 우선순위 문제 ID 집합 (찜한 문제)

        Returns:
            추천 문제 (없으면 None)
        """
        pass