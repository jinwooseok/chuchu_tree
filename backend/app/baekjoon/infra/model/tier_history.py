from datetime import datetime
from sqlalchemy import String, DateTime, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class TierHistory(Base):
    __tablename__ = "tier_history"
    __table_args__ = {'comment': '티어 변경 히스토리'}

    tier_history_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    bj_account_id: Mapped[str] = mapped_column(String(50), ForeignKey('bj_account.bj_account_id'), nullable=False)
    prev_tier_id: Mapped[int] = mapped_column(Integer, ForeignKey('tier.tier_id'), nullable=False)
    changed_tier_id: Mapped[int] = mapped_column(Integer, ForeignKey('tier.tier_id'), nullable=False)
    changed_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
