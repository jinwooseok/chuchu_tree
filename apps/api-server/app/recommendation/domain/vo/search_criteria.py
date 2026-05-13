from dataclasses import dataclass

from app.common.domain.vo.primitives import TierRange


@dataclass(frozen=True)
class SearchCriteria:
    """문제 추천 검색 조건"""
    tier_range: TierRange
    min_skill_rate: int
    max_skill_rate: int
