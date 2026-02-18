"""Create verification session model

Revision ID: 004
Revises: 003
Create Date: 2026-02-18

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create verification_sessions table
    op.create_table('verification_sessions',
        sa.Column('session_id', sa.String(length=36), nullable=False),
        sa.Column('phone_number', sa.String(length=15), nullable=False),
        sa.Column('code', sa.String(length=10), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('attempts', sa.Integer(), nullable=False),
        sa.Column('verified', sa.Boolean(), nullable=False),
        sa.Column('blocked_until', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('session_id')
    )
    
    # Create indexes for efficient querying
    op.create_index(op.f('ix_verification_sessions_phone_number'), 'verification_sessions', ['phone_number'], unique=False)
    op.create_index(op.f('ix_verification_sessions_created_at'), 'verification_sessions', ['created_at'], unique=False)
    op.create_index(op.f('ix_verification_sessions_expires_at'), 'verification_sessions', ['expires_at'], unique=False)
    op.create_index(op.f('ix_verification_sessions_blocked_until'), 'verification_sessions', ['blocked_until'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_verification_sessions_blocked_until'), table_name='verification_sessions')
    op.drop_index(op.f('ix_verification_sessions_expires_at'), table_name='verification_sessions')
    op.drop_index(op.f('ix_verification_sessions_created_at'), table_name='verification_sessions')
    op.drop_index(op.f('ix_verification_sessions_phone_number'), table_name='verification_sessions')
    op.drop_table('verification_sessions')
