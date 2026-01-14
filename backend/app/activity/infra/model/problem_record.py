from datetime import datetime, date
from typing import Optional
from sqlalchemy import Boolean, DateTime, Integer, ForeignKey, Date, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class ProblemRecordModel(Base):
    __tablename__ = "problem_record"
    __table_args__ = (
        Index('idx_marked_date', 'marked_date'),
        {'comment': '유저의 문제 기록'}
    )

    problem_record_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_account_id: Mapped[int] = mapped_column(Integer, ForeignKey('user_account.user_account_id'), nullable=False)
    problem_id: Mapped[int] = mapped_column(Integer, ForeignKey('problem.problem_id'), nullable=False)
    marked_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    solved_yn: Mapped[bool] = mapped_column(Boolean, nullable=False)
    memo_title: Mapped[str|None] = mapped_column(String(500), nullable=False)
    content: Mapped[str|None] = mapped_column(String(500), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
