from dataclasses import dataclass
from app.core.error_codes import ErrorCode
from app.core.exception import APIException


@dataclass(frozen=True)
class Statistics:
    """Value Object - 통계"""
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