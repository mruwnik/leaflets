"""add campaign models.

Revision ID: b6c80b0ef31e
Revises: 1b0145c2bd35
Create Date: 2016-03-13 01:00:10.230526
"""
from alembic import op
import sqlalchemy as sa
from leaflets.models.campaign import AddressStates


# revision identifiers, used by Alembic.
revision = 'b6c80b0ef31e'
down_revision = '1b0145c2bd35'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('campaigns',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('desc', sa.Text(), nullable=True),
        sa.Column('start', sa.DateTime(), nullable=False),
        sa.Column('created', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    )
    op.create_table('campaign_address',
        sa.Column('campaign_id', sa.Integer(), nullable=False),
        sa.Column('address_id', sa.Integer(), nullable=False),
        sa.Column('modified', sa.DateTime(), nullable=False),
        sa.Column('state', sa.Enum('selected', 'marked', 'removed', name='address_states'), nullable=True),
        sa.ForeignKeyConstraint(['address_id'], ['addresses.id'], ),
        sa.ForeignKeyConstraint(['campaign_id'], ['campaigns.id'], ),
        sa.PrimaryKeyConstraint('campaign_id', 'address_id')
    )


def downgrade():
    db = op.get_bind()
    op.drop_table('campaign_address')
    op.drop_table('campaigns')
    db.execute('DROP TYPE address_states')
