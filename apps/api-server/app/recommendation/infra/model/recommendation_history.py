from datetime import datetime
from typing import Optional
from sqlalchemy import Integer, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class RecommendationHistoryModel(Base):
    __tablename__ = "recommendation_history"
    __table_args__ = {"comment": "문제 추천 히스토리"}

    recommendation_history_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    requester_user_account_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("user_account.user_account_id"), nullable=False
    )
    study_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("study.study_id"), nullable=True
    )
    params: Mapped[dict] = mapped_column(JSON, nullable=False, comment="추천 파라미터")
    recommended_problems: Mapped[list] = mapped_column(JSON, nullable=False, comment="추천받은 문제 목록 (스냅샷)")
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now)
