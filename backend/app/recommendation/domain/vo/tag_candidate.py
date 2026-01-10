"""태그 후보 Value Objects"""

from dataclasses import dataclass
from typing import Iterator

from app.baekjoon.domain.vo.tag_account_stat import TagAccountStat
from app.common.domain.vo.identifiers import TagId
from app.tag.domain.entity.tag import Tag


@dataclass(frozen=True)
class TagCandidate:
    """태그 추천 후보 VO"""
    tag: Tag
    stat: TagAccountStat
    score: float

    @staticmethod
    def create(tag: Tag, stat: TagAccountStat, score: float) -> 'TagCandidate':
        """팩토리 메서드"""
        return TagCandidate(tag=tag, stat=stat, score=score)


@dataclass(frozen=True)
class TagCandidates:
    """태그 후보 컬렉션 VO"""
    _candidates: tuple[TagCandidate, ...]

    @staticmethod
    def empty() -> 'TagCandidates':
        """빈 컬렉션 생성"""
        return TagCandidates(tuple())

    @staticmethod
    def from_list(candidates: list[TagCandidate]) -> 'TagCandidates':
        """리스트로부터 생성"""
        return TagCandidates(tuple(candidates))

    def sorted_by_score(self) -> 'TagCandidates':
        """점수순으로 정렬 (내림차순)"""
        sorted_candidates = sorted(self._candidates, key=lambda x: x.score, reverse=True)
        return TagCandidates(tuple(sorted_candidates))

    def __iter__(self) -> Iterator[TagCandidate]:
        """반복 가능"""
        return iter(self._candidates)

    def __len__(self) -> int:
        """크기 반환"""
        return len(self._candidates)


@dataclass(frozen=True)
class TagStatsMap:
    """태그 통계 맵 VO"""
    _stats: dict[TagId, TagAccountStat]

    @staticmethod
    def from_stats(stats: list[TagAccountStat]) -> 'TagStatsMap':
        """통계 리스트로부터 생성"""
        stats_dict = {stat.tag_id: stat for stat in stats}
        return TagStatsMap(stats_dict)

    def get(self, tag_id: TagId) -> TagAccountStat | None:
        """태그 ID로 통계 조회"""
        return self._stats.get(tag_id)

    def get_or_empty(self, tag_id: TagId) -> TagAccountStat:
        """태그 ID로 통계 조회, 없으면 빈 통계 반환"""
        return self._stats.get(tag_id) or TagAccountStat.empty(tag_id)

    def __contains__(self, tag_id: TagId) -> bool:
        """in 연산자 지원"""
        return tag_id in self._stats
