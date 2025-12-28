from datetime import datetime
from typing import Optional
from sqlalchemy import String, DateTime, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class TagSkillHistory(Base):
    __tablename__ = "tag_skill_history"
    __table_args__ = {'comment': '태그 숙련도 변경 히스토리'}

    tag_skill_history_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    bj_account_id: Mapped[str] = mapped_column(String(50), ForeignKey('bj_account.bj_account_id'), nullable=False)
    tag_id: Mapped[int] = mapped_column(Integer, ForeignKey('tag.tag_id'), nullable=False)
    prev_skill_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('tag_skill.tag_skill_id'), nullable=True)
    changed_skill_id: Mapped[int] = mapped_column(Integer, ForeignKey('tag_skill.tag_skill_id'), nullable=False)
    changed_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
