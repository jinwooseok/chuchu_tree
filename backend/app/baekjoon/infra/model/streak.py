"""Streak Model"""

from datetime import datetime, date
from typing import TYPE_CHECKING
from sqlalchemy import String, DateTime, Integer, ForeignKey, Date, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.baekjoon.infra.model.problem_history import ProblemHistoryModel

class StreakModel(Base):
    __tablename__ = "streak"
    __table_args__ = (
        Index('idx_bj_account_date', 'bj_account_id', 'streak_date'),
        {'comment': '스트릭 정보 (날짜별 푼 문제 수)'}
    )

    streak_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    bj_account_id: Mapped[str] = mapped_column(String(50), ForeignKey('bj_account.bj_account_id'), nullable=False)
    streak_date: Mapped[date] = mapped_column(Date, nullable=False)
    solved_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    
    problem_history: Mapped["ProblemHistoryModel | None"] = relationship(
        "ProblemHistoryModel",
        back_populates="streak",
        uselist=False,
        cascade="all, delete-orphan"
    )