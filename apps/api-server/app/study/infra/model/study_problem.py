from datetime import datetime
from sqlalchemy import DateTime, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class StudyProblemModel(Base):
    __tablename__ = "study_problem"
    __table_args__ = {"comment": "스터디 풀문제"}

    study_problem_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    study_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("study.study_id"), nullable=False
    )
    problem_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("problem.problem_id"), nullable=False
    )
    assigned_by_user_account_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("user_account.user_account_id"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    members: Mapped[list["StudyProblemMemberModel"]] = relationship(  # noqa: F821
        "StudyProblemMemberModel",
        back_populates="study_problem",
        lazy="select",
    )
