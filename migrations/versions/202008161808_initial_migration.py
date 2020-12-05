"""Initial migration

Revision ID: fc15cf1faa71
Revises: 
Create Date: 2020-08-16 18:08:19.736624

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'fc15cf1faa71'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('book',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('book')
