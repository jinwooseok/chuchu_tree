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

    def weighted_random_sample(self, k: int) -> 'TagCandidates':
        """점수 기반 가중치 랜덤 샘플링 (중복 없음)

        Args:
            k: 샘플링할 개수

        Returns:
            샘플링된 태그 후보 컬렉션
        """
        import random

        # k가 전체 개수보다 크거나 같으면 전체 반환
        if len(self._candidates) <= k:
            return self

        # 빈 경우 처리
        if len(self._candidates) == 0:
            return self

        # 점수를 가중치로 변환 (최소값 0.1 보장)
        candidates_list = list(self._candidates)
        weights = [max(c.score, 0.1) for c in candidates_list]

        total_weight = sum(weights)

        # 누적 가중치 계산
        cumulative_weights = []
        cum_sum = 0
        for w in weights:
            cum_sum += w
            cumulative_weights.append(cum_sum)

        # k개 샘플링 (중복 없음)
        sampled_indices = set()
        sampled = []
        attempts = 0
        max_attempts = k * 100  # 무한 루프 방지

        while len(sampled) < k and attempts < max_attempts:
            attempts += 1
            r = random.uniform(0, total_weight)

            for i, cum_w in enumerate(cumulative_weights):
                if r <= cum_w and i not in sampled_indices:
                    sampled_indices.add(i)
                    sampled.append(candidates_list[i])
                    break

        return TagCandidates(tuple(sampled))

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
