"""add visibility Model Company

Revision ID: dbc300914575
Revises: 90a15ad887e6
Create Date: 2024-04-27 18:46:31.401512

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'dbc300914575'
down_revision: Union[str, None] = '90a15ad887e6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('companies', sa.Column('visibility', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('companies', 'visibility')
    # ### end Alembic commands ###
