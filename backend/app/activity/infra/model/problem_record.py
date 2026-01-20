from datetime import datetime, date
from typing import TYPE_CHECKING, Optional
from sqlalchemy import Boolean, DateTime, Integer, ForeignKey, Date, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.user.infra.model.user_account import UserAccountModel


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
    order: Mapped[int] = mapped_column(Integer, nullable=False)
    solved_yn: Mapped[bool] = mapped_column(Boolean, nullable=False)
    memo_title: Mapped[str|None] = mapped_column(String(500), nullable=True)
    content: Mapped[str|None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    user_account: Mapped["UserAccountModel"] = relationship(
        "UserAccountModel", 
        back_populates="problem_records"
    )