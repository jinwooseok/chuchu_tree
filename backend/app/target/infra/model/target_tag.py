from datetime import datetime
from typing import Optional
from sqlalchemy import DateTime, Integer, ForeignKey, Boolean, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class TargetTag(Base):
    __tablename__ = "target_tag"
    __table_args__ = (
        UniqueConstraint('target_id', 'tag_id', name='uk_target_code'),
        {'comment': '목표 별 태그'}
    )

    target_tag_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tag_id: Mapped[int] = mapped_column(Integer, ForeignKey('tag.tag_id'), nullable=False)
    target_id: Mapped[int] = mapped_column(Integer, ForeignKey('target.target_id'), nullable=False)
    active_yn: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
