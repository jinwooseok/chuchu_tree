from datetime import datetime, date
from typing import TYPE_CHECKING, Optional
from sqlalchemy import DateTime, Integer, ForeignKey, Boolean, Date, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.user.infra.model.user_account import UserAccountModel

class WillSolveProblemModel(Base):
    __tablename__ = "will_solve_problem"
    __table_args__ = (
        Index('idx_marked_date', 'marked_date'),
        {'comment': '풀 문제 기록'}
    )

    will_solve_problem_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_account_id: Mapped[int] = mapped_column(Integer, ForeignKey('user_account.user_account_id'), nullable=False)
    problem_id: Mapped[int] = mapped_column(Integer, ForeignKey('problem.problem_id'), nullable=False)
    solved: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    marked_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    order: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    user_account: Mapped["UserAccountModel"] = relationship(
        "UserAccountModel", 
        back_populates="will_solve_problems"
    )