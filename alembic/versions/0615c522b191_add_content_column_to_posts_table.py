"""add content column to posts table

Revision ID: 0615c522b191
Revises: d2d6fbcb9176
Create Date: 2022-01-30 11:48:33.834620

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0615c522b191'
down_revision = 'd2d6fbcb9176'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('posts', sa.Column('content', sa.String(), nullable=False))
    pass


def downgrade():
    op.drop_column('posts', 'content')
    pass
