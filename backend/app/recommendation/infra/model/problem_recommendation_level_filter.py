from datetime import datetime
from typing import Optional
from sqlalchemy import String, DateTime, Integer, ForeignKey, Boolean, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class ProblemRecommendationLevelFilterModel(Base):
    __tablename__ = "problem_recommendation_level_filter"

    filter_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    filter_code: Mapped[str] = mapped_column(String(50), nullable=False, comment='EASY, NORMAL, HARD, EXTREME')
    display_name: Mapped[str] = mapped_column(String(100), nullable=False)
    max_user_tier_diff: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    min_user_tier_diff: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    tag_skill_code: Mapped[str] = mapped_column(String(50), nullable=False, comment='IM, AD, MAS')
    min_tag_skill_rate: Mapped[int] = mapped_column(Integer, nullable=True)
    max_tag_skill_rate: Mapped[int] = mapped_column(Integer, nullable=True)
    active_yn: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
