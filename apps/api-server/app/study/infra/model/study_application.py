from datetime import datetime
from sqlalchemy import DateTime, Integer, ForeignKey, Index, String, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column

from app.common.domain.enums import ApplicationStatus
from app.core.database import Base


class StudyApplicationModel(Base):
    __tablename__ = "study_application"
    __table_args__ = (
        Index('idx_study_application_study', 'study_id', 'status'),
        Index('idx_study_application_applicant', 'applicant_user_account_id'),
        {'comment': '스터디 가입신청'}
    )

    application_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    study_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('study.study_id'), nullable=False
    )
    applicant_user_account_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('user_account.user_account_id'), nullable=False
    )
    status: Mapped[ApplicationStatus] = mapped_column(SQLEnum(ApplicationStatus), nullable=False)
    message: Mapped[str | None] = mapped_column(String(300), nullable=True)
    responded_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
