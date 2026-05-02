"""Domain Value Objects for Collections"""

from dataclasses import dataclass
from typing import Iterator

from app.common.domain.vo.identifiers import ProblemId, TagId


@dataclass(frozen=True)
class ProblemIdSet:
    """문제 ID 집합을 관리하는 VO"""
    _ids: frozenset[ProblemId]

    @staticmethod
    def empty() -> 'ProblemIdSet':
        """빈 집합 생성"""
        return ProblemIdSet(frozenset())

    @staticmethod
    def from_ids(ids: set[ProblemId]) -> 'ProblemIdSet':
        """ProblemId set으로부터 생성"""
        return ProblemIdSet(frozenset(ids))

    @staticmethod
    def from_values(values: set[int]) -> 'ProblemIdSet':
        """primitive int set으로부터 생성"""
        return ProblemIdSet(frozenset(ProblemId(v) for v in values))

    def contains(self, problem_id: ProblemId) -> bool:
        """문제 ID가 집합에 포함되어 있는지 확인"""
        return problem_id in self._ids

    def union(self, other: 'ProblemIdSet') -> 'ProblemIdSet':
        """두 집합의 합집합"""
        return ProblemIdSet(self._ids | other._ids)

    def __contains__(self, problem_id: ProblemId) -> bool:
        """in 연산자 지원"""
        return problem_id in self._ids

    def __iter__(self) -> Iterator[ProblemId]:
        """반복 가능"""
        return iter(self._ids)

    def __len__(self) -> int:
        """크기 반환"""
        return len(self._ids)

    def __or__(self, other: 'ProblemIdSet') -> 'ProblemIdSet':
        """| 연산자로 합집합"""
        return self.union(other)


@dataclass(frozen=True)
class TagIdSet:
    """태그 ID 집합을 관리하는 VO"""
    _ids: frozenset[TagId]

    @staticmethod
    def empty() -> 'TagIdSet':
        """빈 집합 생성"""
        return TagIdSet(frozenset())

    @staticmethod
    def from_ids(ids: set[TagId]) -> 'TagIdSet':
        """TagId set으로부터 생성"""
        return TagIdSet(frozenset(ids))

    @staticmethod
    def from_values(values: set[int]) -> 'TagIdSet':
        """primitive int set으로부터 생성"""
        return TagIdSet(frozenset(TagId(v) for v in values))

    @staticmethod
    def from_list(ids: list[TagId] | None) -> 'TagIdSet':
        """TagId list로부터 생성 (None이면 빈 집합)"""
        if ids is None:
            return TagIdSet.empty()
        return TagIdSet(frozenset(ids))

    def contains(self, tag_id: TagId) -> bool:
        """태그 ID가 집합에 포함되어 있는지 확인"""
        return tag_id in self._ids

    def is_empty(self) -> bool:
        """집합이 비어있는지 확인"""
        return len(self._ids) == 0

    def __contains__(self, tag_id: TagId) -> bool:
        """in 연산자 지원"""
        return tag_id in self._ids

    def __iter__(self) -> Iterator[TagId]:
        """반복 가능"""
        return iter(self._ids)

    def __len__(self) -> int:
        """크기 반환"""
        return len(self._ids)

    def __bool__(self) -> bool:
        """bool 변환 (비어있지 않으면 True)"""
        return len(self._ids) > 0
