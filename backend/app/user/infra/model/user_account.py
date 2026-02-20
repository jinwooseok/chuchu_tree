from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, DateTime, Enum as SQLEnum, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.activity.infra.model.user_problem_status import UserProblemStatusModel
from app.common.domain.enums import Provider
from app.core.database import Base

if TYPE_CHECKING:
    from app.user.infra.model.account_link import AccountLinkModel
    from app.user.infra.model.user_target import UserTargetModel
    from app.activity.infra.model.tag_custom import TagCustomModel

class UserAccountModel(Base):
    __tablename__ = "user_account"
    __table_args__ = (
        Index('idx_provider_id', 'provider', 'provider_id'),
        {'comment': '유저 계정'}
    )

    user_account_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    provider: Mapped[Provider] = mapped_column(SQLEnum(Provider), nullable=False)
    provider_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    profile_image: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    registered_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    account_links: Mapped[list["AccountLinkModel"]] = relationship(
        "AccountLinkModel",
        back_populates="user_account",
        cascade="all, delete-orphan"
    )

    targets: Mapped[list["UserTargetModel"]] = relationship(
        "UserTargetModel",
        back_populates="user_account",
        cascade="all, delete-orphan"
    )

    tag_customs: Mapped[list["TagCustomModel"]] = relationship(
        "TagCustomModel",
        back_populates="user_account",
        cascade="all, delete-orphan"
    )

    problem_statuses: Mapped[list["UserProblemStatusModel"]] = relationship(
        "UserProblemStatusModel",
        back_populates="user_account",
        cascade="all, delete-orphan"
    )
    
