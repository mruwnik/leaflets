"""Add a user table.

Revision ID: 968117d87390
Revises:
Create Date: 2016-03-06 15:45:00.971082
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'init'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=256), nullable=False),
        sa.Column('email', sa.String(length=256), nullable=False),
        sa.Column('password_hash', sa.Binary(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('username')
    )


def downgrade():
    op.drop_table('users')

