"""add content column to posts table

Revision ID: 6925cc745510
Revises: 442cd684e654
Create Date: 2023-11-08 20:30:27.079192

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6925cc745510'
down_revision: Union[str, None] = '442cd684e654'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('posts', sa.Column('content', sa.String, nullable=False))


def downgrade() -> None:
    op.drop_column('posts', 'content')
