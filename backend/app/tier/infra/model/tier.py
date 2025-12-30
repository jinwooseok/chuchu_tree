from datetime import datetime
from typing import Optional
from sqlalchemy import String, DateTime, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Tier(Base):
    __tablename__ = "tier"
    __table_args__ = (
        UniqueConstraint('tier_level', 'tier_code', name='uk_tier_level_code'),
        {'comment': '티어 메타 정보'}
    )

    tier_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tier_level: Mapped[int] = mapped_column(Integer, nullable=False)
    tier_code: Mapped[str] = mapped_column(String(50), nullable=False)
    tier_rating: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
