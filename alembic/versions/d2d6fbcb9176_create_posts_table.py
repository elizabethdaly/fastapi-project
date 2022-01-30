"""create posts table

Revision ID: d2d6fbcb9176
Revises: 
Create Date: 2022-01-29 18:39:52.188132

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd2d6fbcb9176'
down_revision = None
branch_labels = None
depends_on = None

# to handle changes
def upgrade():
    op.create_table(
        'posts', sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('title', sa.String(), nullable=False)
        )
    pass

# to undo the changes above
def downgrade():
    op.drop_table('posts')

    pass
