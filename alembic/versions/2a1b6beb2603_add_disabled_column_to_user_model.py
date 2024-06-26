"""Add disabled column to User model

Revision ID: 2a1b6beb2603
Revises: 50aedad803c3
Create Date: 2024-04-21 17:51:32.570483

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2a1b6beb2603'
down_revision: Union[str, None] = '50aedad803c3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('disabled', sa.Boolean(), nullable=True))
    op.drop_index('ix_users_id', table_name='users')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index('ix_users_id', 'users', ['id'], unique=False)
    op.drop_column('users', 'disabled')
    # ### end Alembic commands ###
