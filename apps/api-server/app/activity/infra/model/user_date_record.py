"""UserDateRecord Model - 유저 단위 날짜별 풀이 수 기록"""

from datetime import datetime, date
from typing import Optional
from sqlalchemy import DateTime, Integer, ForeignKey, Date, Index, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class UserDateRecordModel(Base):
    """유저가 특정 날짜에 푼 문제 수 기록 (streak 대체재)

    - user_account + bj_account 단위 (계정 변경 시 데이터 분리)
    - WILL_SOLVE 무관, SOLVED만 추적
    - UNIQUE(user_account_id, bj_account_id, marked_date)
    """
    __tablename__ = "user_date_record"
    __table_args__ = (
        UniqueConstraint('user_account_id', 'bj_account_id', 'marked_date', name='uk_user_date'),
        Index('idx_user_date_record', 'user_account_id', 'bj_account_id', 'marked_date'),
        {'comment': '유저 단위 날짜별 풀이 수 기록 (streak 대체재)'}
    )

    user_date_record_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_account_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('user_account.user_account_id'),
        nullable=False
    )
    bj_account_id: Mapped[str] = mapped_column(
        String(50),
        ForeignKey('bj_account.bj_account_id'),
        nullable=False
    )
    marked_date: Mapped[date] = mapped_column(Date, nullable=False)
    solved_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )
