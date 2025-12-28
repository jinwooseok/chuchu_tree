from datetime import datetime
from typing import Optional
from sqlalchemy import DateTime, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class UserTarget(Base):
    __tablename__ = "user_target"
    __table_args__ = (
        UniqueConstraint('user_account_id', 'target_id', 'deleted_at', name='uk_user_target'),
        {'comment': '유저 목표'}
    )

    user_target_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_account_id: Mapped[int] = mapped_column(Integer, ForeignKey('user_account.user_account_id'), nullable=False)
    target_id: Mapped[int] = mapped_column(Integer, ForeignKey('target.target_id'), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
