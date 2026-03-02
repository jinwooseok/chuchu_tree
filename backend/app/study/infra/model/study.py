from datetime import datetime
from sqlalchemy import String, DateTime, Integer, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class StudyModel(Base):
    __tablename__ = "study"
    __table_args__ = (
        UniqueConstraint('study_name', name='uk_study_name'),
        Index('idx_study_owner', 'owner_user_account_id'),
        {'comment': '스터디'}
    )

    study_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    study_name: Mapped[str] = mapped_column(String(50), nullable=False)
    owner_user_account_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('user_account.user_account_id'), nullable=False
    )
    description: Mapped[str | None] = mapped_column(String(200), nullable=True)
    max_members: Mapped[int] = mapped_column(Integer, nullable=False, default=10)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    members: Mapped[list["StudyMemberModel"]] = relationship(
        "StudyMemberModel",
        back_populates="study",
        cascade="all, delete-orphan",
    )
