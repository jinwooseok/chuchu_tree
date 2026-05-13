"""rename_recommended_problem_ids_to_recommended_problems

Revision ID: g8c9d0e1f2a3
Revises: f7b8c9d0e1f2
Create Date: 2026-03-07 00:00:00.000000

변경 내용:
1. recommendation_history.recommended_problem_ids → recommended_problems (전체 문제 스냅샷)
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


revision: str = "g8c9d0e1f2a3"
down_revision: Union[str, Sequence[str], None] = "f7b8c9d0e1f2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _insp():
    return sa.inspect(op.get_bind())


def _column_exists(table: str, column: str) -> bool:
    return any(c["name"] == column for c in _insp().get_columns(table))


def upgrade() -> None:
    if _column_exists("recommendation_history", "recommended_problem_ids"):
        op.alter_column(
            "recommendation_history",
            "recommended_problem_ids",
            new_column_name="recommended_problems",
            existing_type=mysql.JSON(),
            nullable=False,
        )


def downgrade() -> None:
    if _column_exists("recommendation_history", "recommended_problems"):
        op.alter_column(
            "recommendation_history",
            "recommended_problems",
            new_column_name="recommended_problem_ids",
            existing_type=mysql.JSON(),
            nullable=False,
        )
