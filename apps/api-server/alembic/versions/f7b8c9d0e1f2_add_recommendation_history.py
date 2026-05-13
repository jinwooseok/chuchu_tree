"""add_recommendation_history

Revision ID: f7b8c9d0e1f2
Revises: e5f6a7b8c9d0
Create Date: 2026-03-07 00:00:00.000000

변경 내용:
1. recommendation_history 테이블 생성
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


revision: str = "f7b8c9d0e1f2"
down_revision: Union[str, Sequence[str], None] = "e5f6a7b8c9d0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _insp():
    return sa.inspect(op.get_bind())


def _table_exists(name: str) -> bool:
    return _insp().has_table(name)


def upgrade() -> None:
    if not _table_exists("recommendation_history"):
        op.create_table(
            "recommendation_history",
            sa.Column("recommendation_history_id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("requester_user_account_id", sa.Integer(), nullable=False),
            sa.Column("study_id", sa.Integer(), nullable=True),
            sa.Column("params", mysql.JSON(), nullable=False),
            sa.Column("recommended_problem_ids", mysql.JSON(), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.ForeignKeyConstraint(["requester_user_account_id"], ["user_account.user_account_id"]),
            sa.ForeignKeyConstraint(["study_id"], ["study.study_id"]),
            sa.PrimaryKeyConstraint("recommendation_history_id"),
            comment="문제 추천 히스토리",
        )
        op.create_index(
            "idx_rh_user_account_id",
            "recommendation_history",
            ["requester_user_account_id", "study_id"],
        )
        op.create_index(
            "idx_rh_study_id",
            "recommendation_history",
            ["study_id"],
        )


def downgrade() -> None:
    try:
        op.drop_index("idx_rh_study_id", table_name="recommendation_history")
    except Exception:
        pass
    try:
        op.drop_index("idx_rh_user_account_id", table_name="recommendation_history")
    except Exception:
        pass
    try:
        op.drop_table("recommendation_history")
    except Exception:
        pass
