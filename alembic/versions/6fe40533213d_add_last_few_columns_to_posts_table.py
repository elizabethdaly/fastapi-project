"""add last few columns to posts table

Revision ID: 6fe40533213d
Revises: 0c3a6927ceb9
Create Date: 2022-01-30 12:48:50.480726

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6fe40533213d'
down_revision = '0c3a6927ceb9'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('posts', sa.Column('published', sa.Boolean(), nullable=False, server_default='TRUE'),)
    op.add_column('posts', sa.Column('created_at', sa.TIMESTAMP(timezone=True), 
        nullable=False, server_default=sa.text('NOW()')),)
    pass

def downgrade():
    op.drop_column('posts', 'published')
    op.drop_column('posts', 'created_at')
    pass
