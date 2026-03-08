from datetime import datetime
from sqlalchemy import DateTime, Integer, ForeignKey, Index, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column

from app.common.domain.enums import InvitationStatus
from app.core.database import Base


class StudyInvitationModel(Base):
    __tablename__ = "study_invitation"
    __table_args__ = (
        Index('idx_study_invitation_study', 'study_id', 'status'),
        Index('idx_study_invitation_invitee', 'invitee_user_account_id'),
        {'comment': '스터디 초대'}
    )

    invitation_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    study_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('study.study_id'), nullable=False
    )
    invitee_user_account_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('user_account.user_account_id'), nullable=False
    )
    inviter_user_account_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('user_account.user_account_id'), nullable=False
    )
    status: Mapped[InvitationStatus] = mapped_column(SQLEnum(InvitationStatus), nullable=False)
    responded_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
