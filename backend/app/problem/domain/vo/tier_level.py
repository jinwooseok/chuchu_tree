from dataclasses import dataclass

from app.core.error_codes import ErrorCode
from app.core.exception import APIException


@dataclass(frozen=True)
class TierLevel:
    """Value Object - 티어 레벨"""
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