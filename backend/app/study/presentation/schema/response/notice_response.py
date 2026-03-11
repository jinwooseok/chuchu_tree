from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

from app.study.application.query.notice_query import NoticeQuery


class NoticeItemResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    notice_id: int
    category: str
    category_detail: str | None
    is_read: bool
    created_at: str
    message: str
    content: dict

    @classmethod
    def from_query(cls, q: NoticeQuery) -> "NoticeItemResponse":
        return cls(
            notice_id=q.notice_id,
            category=q.category,
            category_detail=q.category_detail,
            is_read=q.is_read,
            created_at=q.created_at,
            message=q.message,
            content=q.content,
        )


class MyNoticesResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    notices: list[NoticeItemResponse]

    @classmethod
    def from_query(cls, queries: list[NoticeQuery]) -> "MyNoticesResponse":
        return cls(notices=[NoticeItemResponse.from_query(q) for q in queries])
