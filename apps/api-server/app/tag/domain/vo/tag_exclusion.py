from dataclasses import dataclass

from app.common.domain.enums import ExcludedReason
from app.core.error_codes import ErrorCode
from app.core.exception import APIException

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

