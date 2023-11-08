"""add foreign-key to posts table

Revision ID: 1f8393467670
Revises: aeea0f5ce1ec
Create Date: 2023-11-08 20:52:55.783754

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1f8393467670'
down_revision: Union[str, None] = 'aeea0f5ce1ec'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('posts', sa.Column('owner_id', sa.Integer, nullable=False))
    op.create_foreign_key('posts_users_fk', source_table="posts", referent_table="users",
                                            local_cols=['owner_id'], remote_cols=['id'],
                                            ondelete="CASCADE")

def downgrade() -> None:
    op.drop_constraint('posts_users_fk', table_name='posts')
    op.drop_column('posts', 'owner_id')
