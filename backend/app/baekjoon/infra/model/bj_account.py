from datetime import datetime, date
from typing import Optional
from sqlalchemy import String, DateTime, Integer, ForeignKey, Date
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class BjAccountModel(Base):
    __tablename__ = "bj_account"
    __table_args__ = {'comment': '백준 계정'}

    bj_account_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    tier_start_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    tier_id: Mapped[int] = mapped_column(Integer, ForeignKey('tier.tier_id'), nullable=False)
    rating: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    contribution_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    class_: Mapped[int] = mapped_column("class", Integer, nullable=False, default=0)
    longest_streak: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
