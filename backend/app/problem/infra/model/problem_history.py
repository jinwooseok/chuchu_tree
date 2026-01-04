from datetime import datetime
from typing import Optional
from sqlalchemy import String, DateTime, Integer, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class ProblemHistoryModel(Base):
    __tablename__ = "problem_history"
    __table_args__ = (
        Index('idx_solved_at', 'solved_at'),
        {'comment': '문제 해결 히스토리'}
    )

    problem_history_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    bj_account_id: Mapped[str] = mapped_column(String(50), ForeignKey('bj_account.bj_account_id'), nullable=False)
    problem_id: Mapped[int] = mapped_column(Integer, ForeignKey('problem.problem_id'), nullable=False)
    solved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
