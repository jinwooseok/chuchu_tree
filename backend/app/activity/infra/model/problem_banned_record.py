from datetime import datetime
from typing import TYPE_CHECKING, Optional
from sqlalchemy import DateTime, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.user.infra.model.user_account import UserAccountModel

class ProblemBannedRecordModel(Base):
    __tablename__ = "problem_banned_record"
    __table_args__ = {'comment': '유저의 문제 제외 기록'}

    problem_banned_record_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    problem_id: Mapped[int] = mapped_column(Integer, ForeignKey('problem.problem_id'), nullable=False)
    user_account_id: Mapped[int] = mapped_column(Integer, ForeignKey('user_account.user_account_id'), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    user_account: Mapped["UserAccountModel"] = relationship(
        "UserAccountModel", 
        back_populates="banned_problems"
    )