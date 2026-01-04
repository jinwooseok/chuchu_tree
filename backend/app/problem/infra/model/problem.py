from datetime import datetime
from typing import Optional
from sqlalchemy import String, DateTime, Integer, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class ProblemModel(Base):
    __tablename__ = "problem"
    __table_args__ = (
        Index('idx_problem_tier_level', 'problem_tier_level'),
        {'comment': '문제 메타 정보'}
    )

    problem_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    problem_title: Mapped[str] = mapped_column(String(500), nullable=False)
    problem_tier_level: Mapped[int] = mapped_column(Integer, ForeignKey('tier.tier_id'), nullable=False)
    class_level: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
