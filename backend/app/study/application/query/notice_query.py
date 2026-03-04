from dataclasses import dataclass, field


@dataclass
class NoticeQuery:
    notice_id: int
    category: str
    is_read: bool
    created_at: str
    content: dict = field(default_factory=dict)
