from datetime import date, datetime
from sqlalchemy import Date, DateTime, Integer, ForeignKey, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class StudyProblemMemberModel(Base):
    __tablename__ = "study_problem_member"
    __table_args__ = (
        UniqueConstraint("study_problem_id", "user_account_id", name="uq_spm_problem_user"),
        Index("idx_spm_user_date", "user_account_id", "target_date"),
        {"comment": "스터디 풀문제 멤버"},
    )

    study_problem_member_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    study_problem_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("study_problem.study_problem_id"), nullable=False
    )
    user_account_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("user_account.user_account_id"), nullable=False
    )
    target_date: Mapped[date] = mapped_column(Date, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    study_problem: Mapped["StudyProblemModel"] = relationship(back_populates="members")  # noqa: F821
