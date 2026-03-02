from dataclasses import dataclass
from datetime import datetime

from app.common.domain.enums import NoticeCategory
from app.common.domain.vo.identifiers import NoticeId, UserAccountId


@dataclass
class Notice:
    notice_id: NoticeId | None
    recipient_user_account_id: UserAccountId
    category: NoticeCategory
    title: str
    content: dict
    is_read: bool
    reference_id: int | None
    reference_type: str | None
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None

    @classmethod
    def create(
        cls,
        recipient_user_account_id: UserAccountId,
        category: NoticeCategory,
        title: str,
        content: dict,
        reference_id: int | None = None,
        reference_type: str | None = None,
    ) -> "Notice":
        now = datetime.now()
        return cls(
            notice_id=None,
            recipient_user_account_id=recipient_user_account_id,
            category=category,
            title=title,
            content=content,
            is_read=False,
            reference_id=reference_id,
            reference_type=reference_type,
            created_at=now,
            updated_at=now,
            deleted_at=None,
        )

    def mark_as_read(self) -> None:
        self.is_read = True
        self.updated_at = datetime.now()
