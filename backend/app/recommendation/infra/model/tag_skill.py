from datetime import datetime
from typing import Optional
from sqlalchemy import String, DateTime, Integer, ForeignKey, Boolean, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class TagSkillModel(Base):
    __tablename__ = "tag_skill"
    __table_args__ = (
        UniqueConstraint('tag_level', 'tag_skill_code', name='uk_tag_skill'),
        {'comment': '태그 숙련도'}
    )

    tag_skill_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tag_level: Mapped[str] = mapped_column(String(50), nullable=False, comment='NEWBIE, BEGINNER, REQUIREMENT, DETAIL, CHALLENGE')
    tag_skill_code: Mapped[str] = mapped_column(String(50), nullable=False, comment='IM, AD, MAS')
    min_solved_problem: Mapped[int] = mapped_column(Integer, nullable=False)
    min_user_tier: Mapped[int] = mapped_column(Integer, ForeignKey('tier.tier_id'), nullable=False)
    min_solved_problem_tier: Mapped[int] = mapped_column(Integer, ForeignKey('tier.tier_id'), nullable=False)
    active_yn: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
