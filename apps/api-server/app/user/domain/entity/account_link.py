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
    is_synced: bool = False

    @staticmethod
    def create(
        user_account_id: UserAccountId,
        bj_account_id: 'BaekjoonAccountId',
        is_synced: bool = False
    ) -> 'AccountLink':
        return AccountLink(
            account_link_id=None,
            user_account_id=user_account_id,
            bj_account_id=bj_account_id,
            created_at=datetime.now(),
            deleted_at=None,
            is_synced=is_synced
        )

    def mark_as_deleted(self) -> None:
        self.deleted_at = datetime.now()

    def mark_as_synced(self) -> None:
        self.is_synced = True