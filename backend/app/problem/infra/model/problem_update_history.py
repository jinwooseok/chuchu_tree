from datetime import datetime
from sqlalchemy import DateTime, Integer, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class ProblemUpdateHistoryModel(Base):
    __tablename__ = "problem_update_history"
    __table_args__ = {'comment': '문제 변경 정보'}

    problem_update_history_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    problem_id: Mapped[int] = mapped_column(Integer, ForeignKey('problem.problem_id'), nullable=False)
    problem_update_log: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
