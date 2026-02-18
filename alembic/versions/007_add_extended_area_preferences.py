"""add extended area preferences

Revision ID: 007
Revises: 006
Create Date: 2026-02-19

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '007'
down_revision = '006'
branch_labels = None
depends_on = None


def upgrade():
    """Add extended area preferences and statistics to driver_profiles table."""
    # Add extended area preference fields
    op.add_column('driver_profiles', sa.Column('accept_extended_area', sa.Boolean(), nullable=False, server_default='1'))
    op.add_column('driver_profiles', sa.Column('accept_parcel_delivery', sa.Boolean(), nullable=False, server_default='1'))
    
    # Add extended area statistics fields
    op.add_column('driver_profiles', sa.Column('extended_area_ride_count', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('driver_profiles', sa.Column('total_ride_count', sa.Integer(), nullable=False, server_default='0'))


def downgrade():
    """Remove extended area preferences and statistics from driver_profiles table."""
    op.drop_column('driver_profiles', 'total_ride_count')
    op.drop_column('driver_profiles', 'extended_area_ride_count')
    op.drop_column('driver_profiles', 'accept_parcel_delivery')
    op.drop_column('driver_profiles', 'accept_extended_area')
