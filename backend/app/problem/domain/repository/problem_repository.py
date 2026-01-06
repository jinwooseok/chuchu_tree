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
    
    @abstractmethod
    async def find_by_id_prefix(self, prefix: str, limit: int = 5) -> list[Problem]:
        """문제 ID가 특정 문자열로 시작하는 문제들을 조회"""
        pass

    @abstractmethod
    async def find_by_title_keyword(self, keyword: str, limit: int = 5) -> list[Problem]:
        """문제 제목에 키워드가 포함된 문제들을 조회"""
        pass