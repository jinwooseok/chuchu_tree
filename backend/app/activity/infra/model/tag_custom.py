from datetime import datetime
from typing import TYPE_CHECKING, Optional
from sqlalchemy import String, DateTime, Integer, ForeignKey, Boolean, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.user.infra.model.user_account import UserAccountModel

if TYPE_CHECKING:
    from app.user.infra.model.user_account import UserAccountModel

class TagCustomModel(Base):
    __tablename__ = "tag_custom"
    __table_args__ = (
        UniqueConstraint('user_account_id', 'tag_id', 'deleted_at', name='uk_user_tag'),
        {'comment': '태그 커스텀'}
    )

    tag_custom_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_account_id: Mapped[int] = mapped_column(Integer, ForeignKey('user_account.user_account_id'), nullable=False)
    tag_id: Mapped[int] = mapped_column(Integer, ForeignKey('tag.tag_id'), nullable=False)
    excluded_yn: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    excluded_reason: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, comment='INSIGNIFICANT, COMPREHENSIVE, MINOR')
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    user_account: Mapped["UserAccountModel"] = relationship(
        "UserAccountModel", 
        back_populates="tag_customs"
    )