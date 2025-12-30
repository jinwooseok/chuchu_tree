from datetime import datetime
from typing import Optional
from sqlalchemy import String, DateTime, Enum as SQLEnum, Index
from sqlalchemy.orm import Mapped, mapped_column
import enum

from app.core.database import Base


class ProviderEnum(str, enum.Enum):
    KAKAO = "KAKAO"
    NAVER = "NAVER"
    GOOGLE = "GOOGLE"
    NONE = "NONE"


class UserAccount(Base):
    __tablename__ = "user_account"
    __table_args__ = (
        Index('idx_provider_id', 'provider', 'provider_id'),
        {'comment': '유저 계정'}
    )

    user_account_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    provider: Mapped[ProviderEnum] = mapped_column(SQLEnum(ProviderEnum), nullable=False)
    provider_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    registered_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
