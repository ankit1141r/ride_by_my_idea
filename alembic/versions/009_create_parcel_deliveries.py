"""create parcel deliveries table

Revision ID: 009
Revises: 008
Create Date: 2026-02-19

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSON


# revision identifiers, used by Alembic.
revision = '009'
down_revision = '008'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'parcel_deliveries',
        sa.Column('delivery_id', sa.String(36), primary_key=True),
        sa.Column('sender_id', sa.String(36), nullable=False, index=True),
        sa.Column('recipient_phone', sa.String(15), nullable=False),
        sa.Column('recipient_name', sa.String(100), nullable=False),
        sa.Column('driver_id', sa.String(36), nullable=True, index=True),
        
        # Locations
        sa.Column('pickup_location', JSON, nullable=False),
        sa.Column('delivery_location', JSON, nullable=False),
        
        # Parcel details
        sa.Column('parcel_size', sa.Enum('SMALL', 'MEDIUM', 'LARGE', name='parcelsize'), nullable=False),
        sa.Column('weight_kg', sa.Float, nullable=False),
        sa.Column('description', sa.String(500), nullable=True),
        sa.Column('special_instructions', sa.Text, nullable=True),
        sa.Column('is_fragile', sa.Boolean, default=False, nullable=False),
        sa.Column('is_urgent', sa.Boolean, default=False, nullable=False),
        
        # Fare
        sa.Column('estimated_fare', sa.Float, nullable=False),
        sa.Column('fare_breakdown', JSON, nullable=False),
        sa.Column('final_fare', sa.Float, nullable=True),
        
        # Status
        sa.Column('status', sa.Enum('REQUESTED', 'MATCHED', 'DRIVER_ARRIVING', 'PICKED_UP', 'IN_TRANSIT', 'DELIVERED', 'CANCELLED', name='parcelstatus'), default='REQUESTED', nullable=False, index=True),
        
        # Timestamps
        sa.Column('created_at', sa.DateTime, nullable=False),
        sa.Column('matched_at', sa.DateTime, nullable=True),
        sa.Column('picked_up_at', sa.DateTime, nullable=True),
        sa.Column('delivered_at', sa.DateTime, nullable=True),
        sa.Column('cancelled_at', sa.DateTime, nullable=True),
        sa.Column('estimated_delivery_time', sa.DateTime, nullable=True),
        
        # Confirmations
        sa.Column('pickup_photo_url', sa.String(500), nullable=True),
        sa.Column('pickup_signature', sa.Text, nullable=True),
        sa.Column('delivery_photo_url', sa.String(500), nullable=True),
        sa.Column('delivery_signature', sa.Text, nullable=True),
        
        # Cancellation
        sa.Column('cancellation_reason', sa.String(500), nullable=True),
        sa.Column('cancelled_by', sa.String(36), nullable=True),
        
        # Payment
        sa.Column('payment_status', sa.String(20), default='pending'),
        sa.Column('transaction_id', sa.String(100), nullable=True),
    )


def downgrade():
    op.drop_table('parcel_deliveries')
    op.execute('DROP TYPE parcelsize')
    op.execute('DROP TYPE parcelstatus')
