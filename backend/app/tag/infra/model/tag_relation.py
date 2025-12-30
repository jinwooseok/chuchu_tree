from datetime import datetime
from typing import Optional
from sqlalchemy import DateTime, Integer, ForeignKey, Boolean, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class TagRelation(Base):
    __tablename__ = "tag_relation"
    __table_args__ = (
        UniqueConstraint('leading_tag_id', 'sub_tag_id', name='uk_tag_relation'),
        {'comment': '태그 관계'}
    )

    tag_relation_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    leading_tag_id: Mapped[int] = mapped_column(Integer, ForeignKey('tag.tag_id'), nullable=False)
    sub_tag_id: Mapped[int] = mapped_column(Integer, ForeignKey('tag.tag_id'), nullable=False)
    active_yn: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
