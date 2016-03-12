"""Add an addresses table.

Revision ID: 1b0145c2bd35
Revises: init
Create Date: 2016-03-07 19:20:41.055391
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1b0145c2bd35'
down_revision = 'init'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'addresses',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('house', sa.String(length=1024), nullable=True),
        sa.Column('street', sa.String(length=1024), nullable=True),
        sa.Column('town', sa.String(length=1024), nullable=True),
        sa.Column('postcode', sa.String(length=1024), nullable=True),
        sa.Column('country', sa.String(length=1024), nullable=True),
        sa.Column('lat', sa.Float, nullable=False),
        sa.Column('lon', sa.Float, nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('house', 'street', 'town', 'postcode', 'country', name='unique_address'),
        sa.Index('coords_index', 'lat', 'lon'),
    )


def downgrade():
    op.drop_table('addresses')
