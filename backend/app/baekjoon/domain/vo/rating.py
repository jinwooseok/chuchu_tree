from dataclasses import dataclass

from app.core.error_codes import ErrorCode
from app.core.exception import APIException


@dataclass(frozen=True)
class Rating:
    """Value Object - 레이팅"""
    value: int
    
    def __post_init__(self):
        if self.value < 0:
            raise APIException(ErrorCode.INVALID_INPUT_VALUE)
    
    def is_higher_than(self, other: 'Rating') -> bool:
        return self.value > other.value