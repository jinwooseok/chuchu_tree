from datetime import datetime
from sqlalchemy import Boolean, DateTime, Integer, ForeignKey, Index, String, Enum as SQLEnum
from sqlalchemy.dialects.mysql import JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.common.domain.enums import NoticeCategory
from app.core.database import Base


class NoticeModel(Base):
    __tablename__ = "notice"
    __table_args__ = (
        Index("idx_notice_recipient", "recipient_user_account_id", "is_read", "created_at"),
        {"comment": "알림"},
    )

    notice_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    recipient_user_account_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("user_account.user_account_id"), nullable=False
    )
    category: Mapped[NoticeCategory] = mapped_column(SQLEnum(NoticeCategory), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    content: Mapped[dict] = mapped_column(JSON, nullable=False)
    is_read: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    reference_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    reference_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
