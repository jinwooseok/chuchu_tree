from datetime import datetime

from sqlalchemy import Boolean, DateTime, Index, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class SystemLogModel(Base):
    __tablename__ = "system_log"

    system_log_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    log_type: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    log_data: Mapped[dict] = mapped_column(JSON, nullable=False)
    should_notify: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    notification_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    notification_sent: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        Index("idx_system_log_type", "log_type"),
        Index("idx_system_log_type_status", "log_type", "status"),
        Index("idx_system_log_created", "created_at"),
    )
