from dataclasses import dataclass, field


@dataclass
class NoticeQuery:
    notice_id: int
    category: str
    category_detail: str | None
    is_read: bool
    created_at: str
    message: str
    content: dict = field(default_factory=dict)
