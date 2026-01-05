from abc import ABC, abstractmethod

from app.common.domain.vo.identifiers import ProblemId, TagId
from app.problem.domain.entity.problem import Problem, TierLevel

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