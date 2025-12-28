from dataclasses import dataclass

from app.core.error_codes import ErrorCode
from app.core.exception import APIException
from app.tag.domain.enums import ExcludedReason

@dataclass(frozen=True)
class TagExclusion:
    """Value Object - 태그 제외 정보"""
    excluded: bool
    reason: ExcludedReason|None
    
    @staticmethod
    def is_not_excluded() -> 'TagExclusion':
        return TagExclusion(excluded=False, reason=None)
    
    @staticmethod
    def is_excluded(reason: ExcludedReason) -> 'TagExclusion':
        return TagExclusion(excluded=True, reason=reason)
    
    def __post_init__(self):
        if not self.excluded:
            raise APIException(ErrorCode.INVALID_INPUT_VALUE)

