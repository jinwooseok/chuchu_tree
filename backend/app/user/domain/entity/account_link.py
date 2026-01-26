from dataclasses import dataclass
from datetime import datetime
from app.common.domain.vo.identifiers import AccountLinkId, BaekjoonAccountId
from app.user.domain.entity.user_account import UserAccountId


@dataclass
class AccountLink:
    """Entity - 계정 연동"""
    account_link_id: AccountLinkId | None
    user_account_id: UserAccountId
    bj_account_id: BaekjoonAccountId
    created_at: datetime
    deleted_at: datetime|None = None
    
    @staticmethod
    def create(
        user_account_id: UserAccountId,
        bj_account_id: 'BaekjoonAccountId'
    ) -> 'AccountLink':
        return AccountLink(
            account_link_id=None,
            user_account_id=user_account_id,
            bj_account_id=bj_account_id,
            created_at=datetime.now(),
            deleted_at=None
        )
    
    def mark_as_deleted(self) -> None:
        self.deleted_at = datetime.now()