"""create scheduled rides table

Revision ID: 008
Revises: 007
Create Date: 2026-02-19

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '008'
down_revision = '007'
branch_labels = None
depends_on = None


def upgrade():
    """Create scheduled_rides table."""
    op.create_table(
        'scheduled_rides',
        sa.Column('ride_id', sa.String(36), primary_key=True),
        sa.Column('rider_id', sa.String(36), nullable=False, index=True),
        sa.Column('driver_id', sa.String(36), nullable=True, index=True),
        
        # Locations (JSON)
        sa.Column('pickup_location', sa.JSON(), nullable=False),
        sa.Column('destination', sa.JSON(), nullable=False),
        
        # Scheduling
        sa.Column('scheduled_pickup_time', sa.DateTime(), nullable=False, index=True),
        
        # Fare
        sa.Column('estimated_fare', sa.Float(), nullable=False),
        sa.Column('fare_breakdown', sa.JSON(), nullable=False),
        sa.Column('final_fare', sa.Float(), nullable=True),
        
        # Status
        sa.Column('status', sa.String(20), nullable=False, index=True, server_default='scheduled'),
        
        # Timestamps
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('modified_at', sa.DateTime(), nullable=True),
        sa.Column('matched_at', sa.DateTime(), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('cancelled_at', sa.DateTime(), nullable=True),
        
        # Reminders
        sa.Column('reminder_sent', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('driver_reminder_sent', sa.Boolean(), nullable=False, server_default='0'),
        
        # Cancellation
        sa.Column('cancellation_reason', sa.String(500), nullable=True),
        sa.Column('cancellation_fee', sa.Float(), nullable=True),
        sa.Column('cancelled_by', sa.String(36), nullable=True),
        
        # Payment
        sa.Column('payment_status', sa.String(20), nullable=False, server_default='pending'),
        sa.Column('transaction_id', sa.String(100), nullable=True),
    )
    
    # Create indexes
    op.create_index('ix_scheduled_rides_rider_id', 'scheduled_rides', ['rider_id'])
    op.create_index('ix_scheduled_rides_driver_id', 'scheduled_rides', ['driver_id'])
    op.create_index('ix_scheduled_rides_scheduled_pickup_time', 'scheduled_rides', ['scheduled_pickup_time'])
    op.create_index('ix_scheduled_rides_status', 'scheduled_rides', ['status'])


def downgrade():
    """Drop scheduled_rides table."""
    op.drop_index('ix_scheduled_rides_status', 'scheduled_rides')
    op.drop_index('ix_scheduled_rides_scheduled_pickup_time', 'scheduled_rides')
    op.drop_index('ix_scheduled_rides_driver_id', 'scheduled_rides')
    op.drop_index('ix_scheduled_rides_rider_id', 'scheduled_rides')
    op.drop_table('scheduled_rides')
