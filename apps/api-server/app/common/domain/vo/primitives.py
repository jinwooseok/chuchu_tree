from dataclasses import dataclass

from app.common.domain.vo.identifiers import TierId
from app.core.error_codes import ErrorCode
from app.core.exception import APIException


@dataclass(frozen=True)
class Rating:
    value: int
    
    def __post_init__(self):
        if self.value < 0:
            raise APIException(ErrorCode.INVALID_INPUT_VALUE)
    
    def is_higher_than(self, other: 'Rating') -> bool:
        return self.value > other.value


@dataclass(frozen=True)
class TierLevel:
    value: int
    
    def __post_init__(self):
        if self.value < 0:
            raise APIException(ErrorCode.INVALID_INPUT_VALUE)
    
    def is_higher_than(self, other: 'TierLevel') -> bool:
        return self.value > other.value
    
    def is_lower_than(self, other: 'TierLevel') -> bool:
        return self.value < other.value
    
    def difference(self, other: 'TierLevel') -> int:
        return self.value - other.value


@dataclass(frozen=True)
class Statistics:
    contribution_count: int
    class_level: int
    longest_streak: int
    
    def __post_init__(self):
        if self.contribution_count < 0:
            raise APIException(ErrorCode.INVALID_INPUT_VALUE)
        if self.class_level < 0:
            raise APIException(ErrorCode.INVALID_INPUT_VALUE)
        if self.longest_streak < 0:
            raise APIException(ErrorCode.INVALID_INPUT_VALUE)


@dataclass(frozen=True)
class TierRange:
    """Value Object - 티어 범위"""
    min_tier_id: TierId | None
    max_tier_id: TierId | None
    
    def contains(self, tier_id: TierId) -> bool:
        """티어가 범위 내에 있는지 확인"""
        if self.min_tier_id and tier_id.value < self.min_tier_id.value:
            return False
        if self.max_tier_id and tier_id.value > self.max_tier_id.value:
            return False
        return True
    
    def __post_init__(self):
        if (self.min_tier_id and self.max_tier_id and 
            self.min_tier_id.value > self.max_tier_id.value):
            raise APIException(ErrorCode.INVALID_INPUT_VALUE)
