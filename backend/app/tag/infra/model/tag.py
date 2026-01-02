from datetime import datetime
from typing import Optional
from sqlalchemy import String, DateTime, Integer, ForeignKey, Boolean, JSON, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Tag(Base):
    __tablename__ = "tag"
    __table_args__ = (
        UniqueConstraint('tag_code', name='uk_tag_code'),
        {'comment': '태그'}
    )

    tag_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tag_code: Mapped[str] = mapped_column(String(100), nullable=False)
    tag_display_name: Mapped[str] = mapped_column(String(100), nullable=False)
    tag_level: Mapped[str] = mapped_column(String(50), nullable=False, comment='NEWBIE, BEGINNER, REQUIREMENT, DETAIL, CHALLENGE')
    excluded_yn: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    excluded_reason: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, comment='INSIGNIFICANT, COMPREHENSIVE, MINOR')
    min_problem_tier_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('tier.tier_id'), nullable=True)
    max_problem_tier_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('tier.tier_id'), nullable=True)
    min_solved_person_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    aliases: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    tag_problem_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
