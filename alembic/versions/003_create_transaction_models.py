"""Create transaction and payout models

Revision ID: 003
Revises: 002
Create Date: 2026-02-18

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSON


revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade():
    # Create transactions table
    op.create_table('transactions',
        sa.Column('transaction_id', sa.String(length=100), nullable=False),
        sa.Column('ride_id', sa.String(length=36), nullable=False),
        sa.Column('rider_id', sa.String(length=36), nullable=False),
        sa.Column('driver_id', sa.String(length=36), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('gateway', sa.Enum('RAZORPAY', 'PAYTM', name='paymentgateway'), nullable=False),
        sa.Column('status', sa.Enum('PENDING', 'SUCCESS', 'FAILED', name='transactionstatus'), nullable=False),
        sa.Column('gateway_transaction_id', sa.String(length=100), nullable=True),
        sa.Column('gateway_response', JSON, nullable=True),
        sa.Column('retry_count', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['ride_id'], ['rides.ride_id'], ),
        sa.ForeignKeyConstraint(['rider_id'], ['users.user_id'], ),
        sa.ForeignKeyConstraint(['driver_id'], ['users.user_id'], ),
        sa.PrimaryKeyConstraint('transaction_id')
    )
    
    op.create_index(op.f('ix_transactions_ride_id'), 'transactions', ['ride_id'], unique=False)
    op.create_index(op.f('ix_transactions_rider_id'), 'transactions', ['rider_id'], unique=False)
    op.create_index(op.f('ix_transactions_driver_id'), 'transactions', ['driver_id'], unique=False)
    op.create_index(op.f('ix_transactions_status'), 'transactions', ['status'], unique=False)
    op.create_index(op.f('ix_transactions_created_at'), 'transactions', ['created_at'], unique=False)
    
    # Create driver_payouts table
    op.create_table('driver_payouts',
        sa.Column('payout_id', sa.String(length=100), nullable=False),
        sa.Column('driver_id', sa.String(length=36), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('rides', JSON, nullable=False),
        sa.Column('status', sa.Enum('SCHEDULED', 'PROCESSING', 'COMPLETED', 'FAILED', name='payoutstatus'), nullable=False),
        sa.Column('bank_account', sa.String(length=100), nullable=False),
        sa.Column('gateway_payout_id', sa.String(length=100), nullable=True),
        sa.Column('gateway_response', JSON, nullable=True),
        sa.Column('scheduled_for', sa.DateTime(), nullable=False),
        sa.Column('processed_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['driver_id'], ['users.user_id'], ),
        sa.PrimaryKeyConstraint('payout_id')
    )
    
    op.create_index(op.f('ix_driver_payouts_driver_id'), 'driver_payouts', ['driver_id'], unique=False)
    op.create_index(op.f('ix_driver_payouts_status'), 'driver_payouts', ['status'], unique=False)
    op.create_index(op.f('ix_driver_payouts_scheduled_for'), 'driver_payouts', ['scheduled_for'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_driver_payouts_scheduled_for'), table_name='driver_payouts')
    op.drop_index(op.f('ix_driver_payouts_status'), table_name='driver_payouts')
    op.drop_index(op.f('ix_driver_payouts_driver_id'), table_name='driver_payouts')
    op.drop_table('driver_payouts')
    
    op.drop_index(op.f('ix_transactions_created_at'), table_name='transactions')
    op.drop_index(op.f('ix_transactions_status'), table_name='transactions')
    op.drop_index(op.f('ix_transactions_driver_id'), table_name='transactions')
    op.drop_index(op.f('ix_transactions_rider_id'), table_name='transactions')
    op.drop_index(op.f('ix_transactions_ride_id'), table_name='transactions')
    op.drop_table('transactions')
    
    sa.Enum(name='payoutstatus').drop(op.get_bind(), checkfirst=False)
    sa.Enum(name='transactionstatus').drop(op.get_bind(), checkfirst=False)
    sa.Enum(name='paymentgateway').drop(op.get_bind(), checkfirst=False)
