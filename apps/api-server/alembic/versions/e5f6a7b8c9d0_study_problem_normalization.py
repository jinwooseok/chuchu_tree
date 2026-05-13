"""study_problem_normalization

Revision ID: e5f6a7b8c9d0
Revises: d4e5f6a7b8c9
Create Date: 2026-03-03 00:00:00.000000

변경 내용:
1. study_problem_member 테이블 생성
2. 기존 study_problem.target_user_account_ids JSON 데이터 → study_problem_member rows 마이그레이션
3. study_problem.target_user_account_ids 컬럼 제거
4. study_problem.target_date 컬럼 제거
5. idx_study_problem_study_date 인덱스 제거
6. notice.content 컬럼 TEXT → JSON 변환
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


revision: str = "e5f6a7b8c9d0"
down_revision: Union[str, Sequence[str], None] = "d4e5f6a7b8c9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _insp():
    return sa.inspect(op.get_bind())


def _table_exists(name: str) -> bool:
    return _insp().has_table(name)


def _column_exists(table: str, column: str) -> bool:
    return any(c["name"] == column for c in _insp().get_columns(table))


def _index_exists(table: str, index: str) -> bool:
    return any(i["name"] == index for i in _insp().get_indexes(table))


def upgrade() -> None:
    conn = op.get_bind()

    # =========================================================================
    # 1. study_problem_member 테이블 생성
    # =========================================================================
    if not _table_exists("study_problem_member"):
        op.create_table(
            "study_problem_member",
            sa.Column("study_problem_member_id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("study_problem_id", sa.Integer(), nullable=False),
            sa.Column("user_account_id", sa.Integer(), nullable=False),
            sa.Column("target_date", sa.Date(), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.Column("updated_at", sa.DateTime(), nullable=False),
            sa.Column("deleted_at", sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(["study_problem_id"], ["study_problem.study_problem_id"]),
            sa.ForeignKeyConstraint(["user_account_id"], ["user_account.user_account_id"]),
            sa.PrimaryKeyConstraint("study_problem_member_id"),
            sa.UniqueConstraint("study_problem_id", "user_account_id", name="uq_spm_problem_user"),
            comment="스터디 풀문제 멤버",
        )
    if not _index_exists("study_problem_member", "idx_spm_user_date"):
        op.create_index("idx_spm_user_date", "study_problem_member", ["user_account_id", "target_date"])

    # =========================================================================
    # 2. 기존 JSON 데이터 마이그레이션 → study_problem_member rows
    # =========================================================================
    if _column_exists("study_problem", "target_user_account_ids") and _column_exists("study_problem", "target_date"):
        rows = conn.execute(
            sa.text(
                "SELECT study_problem_id, target_user_account_ids, target_date, created_at, updated_at "
                "FROM study_problem WHERE deleted_at IS NULL"
            )
        ).fetchall()
        now_str = sa.text("NOW()")
        for row in rows:
            sp_id = row[0]
            uid_list = row[1]
            target_date = row[2]
            created_at = row[3]
            updated_at = row[4]
            if uid_list is None:
                continue
            if isinstance(uid_list, str):
                import json
                try:
                    uid_list = json.loads(uid_list)
                except Exception:
                    continue
            if not isinstance(uid_list, list):
                continue
            for uid in uid_list:
                try:
                    conn.execute(
                        sa.text(
                            "INSERT IGNORE INTO study_problem_member "
                            "(study_problem_id, user_account_id, target_date, created_at, updated_at) "
                            "VALUES (:sp_id, :uid, :target_date, :created_at, :updated_at)"
                        ),
                        {
                            "sp_id": sp_id,
                            "uid": uid,
                            "target_date": target_date,
                            "created_at": created_at,
                            "updated_at": updated_at,
                        },
                    )
                except Exception:
                    pass

    # =========================================================================
    # 3. study_problem.target_user_account_ids 컬럼 제거
    # =========================================================================
    if _column_exists("study_problem", "target_user_account_ids"):
        op.drop_column("study_problem", "target_user_account_ids")

    # =========================================================================
    # 4. study_problem.target_date 컬럼 제거
    # =========================================================================
    if _index_exists("study_problem", "idx_study_problem_study_date"):
        # MySQL에서 복합 인덱스(study_id, target_date)가 study_id FK의 supporting index로
        # 사용 중이면 직접 삭제 불가 → study_id 단독 인덱스를 먼저 생성해 FK를 대체한 뒤 삭제
        if not _index_exists("study_problem", "idx_study_problem_study_id"):
            op.create_index("idx_study_problem_study_id", "study_problem", ["study_id"])
        op.drop_index("idx_study_problem_study_date", table_name="study_problem")
    if _column_exists("study_problem", "target_date"):
        op.drop_column("study_problem", "target_date")

    # =========================================================================
    # 5. notice.content 컬럼 TEXT → JSON
    # =========================================================================
    # 기존 text 데이터를 JSON으로 변환 (백필: {"text": "기존내용"})
    conn.execute(
        sa.text(
            "UPDATE notice SET content = JSON_OBJECT('text', content) "
            "WHERE content IS NOT NULL AND JSON_VALID(content) = 0"
        )
    )
    op.alter_column(
        "notice",
        "content",
        existing_type=sa.String(1000),
        type_=mysql.JSON(),
        nullable=False,
    )


def downgrade() -> None:
    conn = op.get_bind()

    # notice.content JSON → TEXT
    op.alter_column(
        "notice",
        "content",
        existing_type=mysql.JSON(),
        type_=sa.String(1000),
        nullable=False,
    )

    # study_problem.target_date 복원
    if not _column_exists("study_problem", "target_date"):
        op.add_column(
            "study_problem",
            sa.Column("target_date", sa.Date(), nullable=True),
        )
    if not _index_exists("study_problem", "idx_study_problem_study_date"):
        op.create_index("idx_study_problem_study_date", "study_problem", ["study_id", "target_date"])

    # study_problem.target_user_account_ids 복원
    if not _column_exists("study_problem", "target_user_account_ids"):
        op.add_column(
            "study_problem",
            sa.Column("target_user_account_ids", mysql.JSON(), nullable=True),
        )

    # study_problem_member 제거
    try:
        op.drop_index("idx_spm_user_date", table_name="study_problem_member")
    except Exception:
        pass
    try:
        op.drop_table("study_problem_member")
    except Exception:
        pass
