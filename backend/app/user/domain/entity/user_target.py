from dataclasses import dataclass
from datetime import datetime
from app.user.domain.entity.user_account import UserAccountId


@dataclass
class UserTarget:
    """Entity - 유저 목표"""
    user_target_id: int|None
    user_account_id: UserAccountId
    target_id: 'TargetId'
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime|None = None
    
    @staticmethod
    def create(user_account_id: UserAccountId, target_id: 'TargetId') -> 'UserTarget':
        now = datetime.now()
        return UserTarget(
            user_target_id=None,
            user_account_id=user_account_id,
            target_id=target_id,
            created_at=now,
            updated_at=now,
            deleted_at=None
        )
    
    def mark_as_deleted(self) -> None:
        self.deleted_at = datetime.now()