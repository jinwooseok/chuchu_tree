from pydantic import BaseModel


class NoticeRequestedPayload(BaseModel):
    recipient_user_account_id: int
    category: str
    category_detail: str
    content: dict
