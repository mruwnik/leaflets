"""Attach users to parents.

Revision ID: 18308b231840
Revises: b6c80b0ef31e
Create Date: 2016-03-31 20:21:00.193710
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '18308b231840'
down_revision = 'b6c80b0ef31e'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('campaign_address', sa.Column('user_id', sa.Integer(), nullable=True))
    op.create_foreign_key('campaign_address_fk', 'campaign_address', 'users', ['user_id'], ['id'])
    op.add_column('users', sa.Column('parent_id', sa.Integer(), nullable=True))
    op.create_foreign_key('users_fk', 'users', 'users', ['parent_id'], ['id'])


def downgrade():
    op.drop_constraint('users_fk', 'users', type_='foreignkey')
    op.drop_column('users', 'parent_id')
    op.drop_constraint('campaign_address_fk', 'campaign_address', type_='foreignkey')
    op.drop_column('campaign_address', 'user_id')
