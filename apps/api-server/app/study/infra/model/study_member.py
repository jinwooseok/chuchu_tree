from datetime import datetime
from sqlalchemy import DateTime, Integer, ForeignKey, UniqueConstraint, Index, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.common.domain.enums import StudyMemberRole
from app.core.database import Base


class StudyMemberModel(Base):
    __tablename__ = "study_member"
    __table_args__ = (
        UniqueConstraint('study_id', 'user_account_id', name='uk_study_member'),
        Index('idx_study_member_user', 'user_account_id'),
        {'comment': '스터디 멤버'}
    )

    study_member_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    study_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('study.study_id'), nullable=False
    )
    user_account_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('user_account.user_account_id'), nullable=False
    )
    role: Mapped[StudyMemberRole] = mapped_column(SQLEnum(StudyMemberRole), nullable=False)
    joined_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    study: Mapped["StudyModel"] = relationship("StudyModel", back_populates="members")
