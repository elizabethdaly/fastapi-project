"""add foreign-key to posts table

Revision ID: 0c3a6927ceb9
Revises: 1f3db43ddb43
Create Date: 2022-01-30 12:21:43.825048

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0c3a6927ceb9'
down_revision = '1f3db43ddb43'
branch_labels = None
depends_on = None

# changes we want to make
def upgrade():
    # ceate the col first
    op.add_column('posts', sa.Column('owner_id', sa.Integer(), nullable=False))
    op.create_foreign_key('post_users_fk', source_table="posts", referent_table="users",
        local_cols=['owner_id'], remote_cols=['id'], ondelete="CASCADE")
    pass

# undo those changes
def downgrade():
    op.drop_constraint('post_users_fk', table_name="posts")
    op.drop_column('posts', 'owner_id')
    pass
