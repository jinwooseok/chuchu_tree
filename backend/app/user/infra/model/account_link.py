from datetime import datetime
from typing import TYPE_CHECKING, Optional
from sqlalchemy import String, DateTime, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.user.infra.model.user_account import UserAccountModel

class AccountLinkModel(Base):
    __tablename__ = "account_link"
    __table_args__ = (
        UniqueConstraint('user_account_id', 'bj_account_id', name='uk_user_bj_account'),
        {'comment': '백준, 유저 계정 간 연동'}
    )

    account_link_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_account_id: Mapped[int] = mapped_column(Integer, ForeignKey('user_account.user_account_id'), nullable=False)
    bj_account_id: Mapped[str] = mapped_column(String(50), ForeignKey('bj_account.bj_account_id'), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    user_account: Mapped["UserAccountModel"] = relationship(
        "UserAccountModel", 
        back_populates="account_links"
    )