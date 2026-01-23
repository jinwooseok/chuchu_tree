"""UserProblemStatus Model - 문제별 마스터 테이블 (1:N 관계의 1)"""
from datetime import datetime
from typing import TYPE_CHECKING, Optional
from sqlalchemy import Boolean, DateTime, Integer, ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.user.infra.model.user_account import UserAccountModel
    from app.activity.infra.model.problem_date_record import ProblemDateRecordModel


class UserProblemStatusModel(Base):
    """유저의 문제별 상태 (마스터 테이블)

    - 사용자와 문제 조합당 단일 레코드
    - banned_yn, solved_yn 등 상태 플래그 관리
    - representative_tag_id, memo_title, content 등 문제별 속성 관리
    """
    __tablename__ = "user_problem_status"
    __table_args__ = (
        UniqueConstraint('user_account_id', 'problem_id', name='uk_user_problem'),
        Index('idx_user_status', 'user_account_id', 'banned_yn', 'solved_yn'),
        {'comment': '유저의 문제별 상태 (마스터)'}
    )

    user_problem_status_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_account_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('user_account.user_account_id'), nullable=False
    )
    problem_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('problem.problem_id'), nullable=False
    )

    # 상태 플래그
    banned_yn: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    solved_yn: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # 문제별 속성 (단일)
    representative_tag_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    memo_title: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    content: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # 타임스탬프
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    user_account: Mapped["UserAccountModel"] = relationship(
        "UserAccountModel",
        back_populates="problem_statuses"
    )

    date_records: Mapped[list["ProblemDateRecordModel"]] = relationship(
        "ProblemDateRecordModel",
        back_populates="user_problem_status",
        cascade="all, delete-orphan"
    )
