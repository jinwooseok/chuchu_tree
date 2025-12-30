from datetime import datetime
from typing import Optional
from sqlalchemy import String, DateTime, Boolean, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Target(Base):
    __tablename__ = "target"
    __table_args__ = (
        UniqueConstraint('target_code', name='uk_target_code'),
        {'comment': '목표 메타 정보'}
    )

    target_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    target_code: Mapped[str] = mapped_column(String(50), nullable=False)
    active_yn: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    target_display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
