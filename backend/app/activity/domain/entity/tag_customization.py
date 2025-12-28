from dataclasses import dataclass
from datetime import datetime

from app.common.domain.vo.identifiers import TagId, UserAccountId
from app.tag.domain.enums import ExcludedReason


@dataclass
class TagCustomization:
    """Entity - 태그 커스터마이징"""
    tag_custom_id: int|None
    user_account_id: UserAccountId
    tag_id: TagId
    excluded: bool
    reason: ExcludedReason|None
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime|None = None
    
    @staticmethod
    def create(
        user_account_id: UserAccountId,
        tag_id: TagId,
        excluded: bool,
        reason: ExcludedReason|None = None
    ) -> 'TagCustomization':
        now = datetime.now()
        return TagCustomization(
            tag_custom_id=None,
            user_account_id=user_account_id,
            tag_id=tag_id,
            excluded=excluded,
            reason=reason,
            created_at=now,
            updated_at=now,
            deleted_at=None
        )