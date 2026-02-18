"""Create user models

Revision ID: 001
Revises: 
Create Date: 2026-02-18

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create users table
    op.create_table('users',
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('phone_number', sa.String(length=15), nullable=False),
        sa.Column('phone_verified', sa.Boolean(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('email', sa.String(length=100), nullable=False),
        sa.Column('user_type', sa.Enum('RIDER', 'DRIVER', name='usertype'), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('average_rating', sa.Float(), nullable=True),
        sa.Column('total_rides', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('user_id'),
        sa.UniqueConstraint('phone_number')
    )
    op.create_index(op.f('ix_users_phone_number'), 'users', ['phone_number'], unique=True)
    
    # Create driver_profiles table
    op.create_table('driver_profiles',
        sa.Column('driver_id', sa.String(length=36), nullable=False),
        sa.Column('license_number', sa.String(length=50), nullable=False),
        sa.Column('license_verified', sa.Boolean(), nullable=True),
        sa.Column('vehicle_registration', sa.String(length=50), nullable=False),
        sa.Column('vehicle_make', sa.String(length=50), nullable=False),
        sa.Column('vehicle_model', sa.String(length=50), nullable=False),
        sa.Column('vehicle_color', sa.String(length=30), nullable=False),
        sa.Column('vehicle_verified', sa.Boolean(), nullable=True),
        sa.Column('insurance_expiry', sa.DateTime(), nullable=False),
        sa.Column('status', sa.Enum('AVAILABLE', 'UNAVAILABLE', 'BUSY', name='driverstatus'), nullable=False),
        sa.Column('total_earnings', sa.Float(), nullable=True),
        sa.Column('daily_availability_hours', sa.Float(), nullable=True),
        sa.Column('availability_start_time', sa.DateTime(), nullable=True),
        sa.Column('cancellation_count', sa.Integer(), nullable=True),
        sa.Column('last_cancellation_reset', sa.DateTime(), nullable=True),
        sa.Column('is_suspended', sa.Boolean(), nullable=True),
        sa.Column('is_flagged', sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(['driver_id'], ['users.user_id'], ),
        sa.PrimaryKeyConstraint('driver_id')
    )
    
    # Create emergency_contacts table
    op.create_table('emergency_contacts',
        sa.Column('contact_id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('phone_number', sa.String(length=15), nullable=False),
        sa.Column('relationship_type', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ),
        sa.PrimaryKeyConstraint('contact_id')
    )


def downgrade() -> None:
    op.drop_table('emergency_contacts')
    op.drop_table('driver_profiles')
    op.drop_index(op.f('ix_users_phone_number'), table_name='users')
    op.drop_table('users')
    sa.Enum(name='driverstatus').drop(op.get_bind(), checkfirst=False)
    sa.Enum(name='usertype').drop(op.get_bind(), checkfirst=False)
