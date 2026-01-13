"""account link unique delete

Revision ID: 558e1f5665c3
Revises: b477d1d9dbf2
Create Date: 2026-01-13 08:19:12.036596

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '558e1f5665c3'
down_revision: Union[str, Sequence[str], None] = 'b477d1d9dbf2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. 외래 키가 사용할 일반 인덱스를 '먼저' 생성합니다.
    # MySQL이 uk_user_bj_account 대신 이 인덱스를 FK용으로 쓰게 만듭니다.
    op.create_index('idx_user_account_id', 'account_link', ['user_account_id'], unique=False)
    op.create_index('idx_bj_account_id', 'account_link', ['bj_account_id'], unique=False)

    # 2. 이제 안전하게 유니크 인덱스를 삭제할 수 있습니다.
    op.drop_index('uk_user_bj_account', table_name='account_link')
    
    # (선택 사항) 코멘트 삭제 로직은 유지하거나 필요에 따라 수정
    op.drop_table_comment('account_link', existing_comment='백준, 유저 계정 간 연동')

def downgrade() -> None:
    # 복구할 때는 유니크 인덱스를 다시 만들고 일반 인덱스를 삭제합니다.
    op.create_index('uk_user_bj_account', 'account_link', ['user_account_id', 'bj_account_id'], unique=True)
    op.drop_index('idx_user_account_id', table_name='account_link')
    op.drop_index('idx_bj_account_id', table_name='account_link')