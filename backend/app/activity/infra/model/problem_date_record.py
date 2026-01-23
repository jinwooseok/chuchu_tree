"""ProblemDateRecord Model - 날짜별 기록 테이블 (1:N 관계의 N)"""
from datetime import datetime, date
from typing import TYPE_CHECKING, Optional
from enum import Enum as PyEnum
from sqlalchemy import DateTime, Integer, ForeignKey, Date, Index, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.activity.infra.model.user_problem_status import UserProblemStatusModel


class RecordType(PyEnum):
    """기록 유형"""
    WILL_SOLVE = "WILL_SOLVE"
    SOLVED = "SOLVED"


class ProblemDateRecordModel(Base):
    """날짜별 문제 기록 (디테일 테이블)

    - UserProblemStatus와 1:N 관계
    - 같은 문제를 여러 날짜에 등록 가능
    - record_type으로 WILL_SOLVE/SOLVED 구분
    """
    __tablename__ = "problem_date_record"
    __table_args__ = (
        Index('idx_marked_date', 'marked_date'),
        Index('idx_status_date', 'user_problem_status_id', 'marked_date'),
        {'comment': '날짜별 문제 기록 (디테일)'}
    )

    problem_date_record_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_problem_status_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('user_problem_status.user_problem_status_id', ondelete='CASCADE'),
        nullable=False
    )

    marked_date: Mapped[date] = mapped_column(Date, nullable=False)
    record_type: Mapped[RecordType] = mapped_column(SQLEnum(RecordType), nullable=False)
    display_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # 타임스탬프
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationship
    user_problem_status: Mapped["UserProblemStatusModel"] = relationship(
        "UserProblemStatusModel",
        back_populates="date_records"
    )
