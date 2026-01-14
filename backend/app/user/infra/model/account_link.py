from datetime import datetime
from typing import TYPE_CHECKING, Optional
from sqlalchemy import String, DateTime, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.user.infra.model.user_account import UserAccountModel

class AccountLinkModel(Base):
    __tablename__ = "account_link"
    
    account_link_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_account_id: Mapped[int] = mapped_column(Integer, ForeignKey('user_account.user_account_id'), nullable=False)
    bj_account_id: Mapped[str] = mapped_column(String(50), ForeignKey('bj_account.bj_account_id'), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    # 인덱스는 마이그레이션 558e1f5665c3에서 수동 생성됨 (idx_user_account_id, idx_bj_account_id)
    
    user_account: Mapped["UserAccountModel"] = relationship(
        "UserAccountModel", 
        back_populates="account_links"
    )