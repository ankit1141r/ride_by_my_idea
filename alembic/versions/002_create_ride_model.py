"""Create ride model

Revision ID: 002
Revises: 001
Create Date: 2026-02-18

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSON


revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('rides',
        sa.Column('ride_id', sa.String(length=36), nullable=False),
        sa.Column('rider_id', sa.String(length=36), nullable=False),
        sa.Column('driver_id', sa.String(length=36), nullable=True),
        sa.Column('status', sa.Enum('REQUESTED', 'MATCHED', 'DRIVER_ARRIVING', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED', name='ridestatus'), nullable=False),
        sa.Column('pickup_location', JSON, nullable=False),
        sa.Column('destination', JSON, nullable=False),
        sa.Column('actual_route', JSON, nullable=True),
        sa.Column('requested_at', sa.DateTime(), nullable=False),
        sa.Column('matched_at', sa.DateTime(), nullable=True),
        sa.Column('pickup_time', sa.DateTime(), nullable=True),
        sa.Column('start_time', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('estimated_fare', sa.Float(), nullable=False),
        sa.Column('final_fare', sa.Float(), nullable=True),
        sa.Column('fare_breakdown', JSON, nullable=False),
        sa.Column('payment_status', sa.Enum('PENDING', 'COMPLETED', 'FAILED', name='paymentstatus'), nullable=False),
        sa.Column('transaction_id', sa.String(length=100), nullable=True),
        sa.Column('rider_rating', sa.Integer(), nullable=True),
        sa.Column('rider_review', sa.String(length=500), nullable=True),
        sa.Column('rider_rating_timestamp', sa.DateTime(), nullable=True),
        sa.Column('driver_rating', sa.Integer(), nullable=True),
        sa.Column('driver_review', sa.String(length=500), nullable=True),
        sa.Column('driver_rating_timestamp', sa.DateTime(), nullable=True),
        sa.Column('cancelled_by', sa.String(length=36), nullable=True),
        sa.Column('cancellation_reason', sa.String(length=500), nullable=True),
        sa.Column('cancellation_fee', sa.Float(), nullable=True),
        sa.Column('cancellation_timestamp', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['rider_id'], ['users.user_id'], ),
        sa.ForeignKeyConstraint(['driver_id'], ['users.user_id'], ),
        sa.PrimaryKeyConstraint('ride_id')
    )
    
    op.create_index(op.f('ix_rides_rider_id'), 'rides', ['rider_id'], unique=False)
    op.create_index(op.f('ix_rides_driver_id'), 'rides', ['driver_id'], unique=False)
    op.create_index(op.f('ix_rides_status'), 'rides', ['status'], unique=False)
    op.create_index(op.f('ix_rides_requested_at'), 'rides', ['requested_at'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_rides_requested_at'), table_name='rides')
    op.drop_index(op.f('ix_rides_status'), table_name='rides')
    op.drop_index(op.f('ix_rides_driver_id'), table_name='rides')
    op.drop_index(op.f('ix_rides_rider_id'), table_name='rides')
    op.drop_table('rides')
    sa.Enum(name='paymentstatus').drop(op.get_bind(), checkfirst=False)
    sa.Enum(name='ridestatus').drop(op.get_bind(), checkfirst=False)
