from dataclasses import dataclass
from datetime import datetime

from app.common.domain.enums import NoticeCategory, NoticeCategoryDetail
from app.common.domain.vo.identifiers import NoticeId, UserAccountId


@dataclass
class Notice:
    notice_id: NoticeId | None
    recipient_user_account_id: UserAccountId
    category: NoticeCategory
    category_detail: NoticeCategoryDetail | None
    content: dict
    is_read: bool
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None

    @classmethod
    def create(
        cls,
        recipient_user_account_id: UserAccountId,
        category: NoticeCategory,
        category_detail: NoticeCategoryDetail | None,
        content: dict,
    ) -> "Notice":
        now = datetime.now()
        return cls(
            notice_id=None,
            recipient_user_account_id=recipient_user_account_id,
            category=category,
            category_detail=category_detail,
            content=content,
            is_read=False,
            created_at=now,
            updated_at=now,
            deleted_at=None,
        )

    def mark_as_read(self) -> None:
        self.is_read = True
        self.updated_at = datetime.now()
