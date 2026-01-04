from datetime import datetime, date
from typing import Optional
from sqlalchemy import DateTime, Integer, ForeignKey, Boolean, Date, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class WillSolveProblemModel(Base):
    __tablename__ = "will_solve_problem"
    __table_args__ = (
        Index('idx_marked_date', 'marked_date'),
        {'comment': '풀 문제 기록'}
    )

    will_solve_problem_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_account_id: Mapped[int] = mapped_column(Integer, ForeignKey('user_account.user_account_id'), nullable=False)
    problem_id: Mapped[int] = mapped_column(Integer, ForeignKey('problem.problem_id'), nullable=False)
    marked_yn: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    marked_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
