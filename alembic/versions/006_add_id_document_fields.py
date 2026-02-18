"""add id document fields to driver profile

Revision ID: 006
Revises: 005
Create Date: 2024-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '006'
down_revision = '005'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add ID document fields to driver_profiles table."""
    op.add_column('driver_profiles', sa.Column('id_document_path', sa.String(500), nullable=True))
    op.add_column('driver_profiles', sa.Column('id_document_type', sa.String(50), nullable=True))
    op.add_column('driver_profiles', sa.Column('id_document_uploaded_at', sa.DateTime(), nullable=True))
    op.add_column('driver_profiles', sa.Column('id_verification_status', sa.String(20), server_default='pending', nullable=True))


def downgrade() -> None:
    """Remove ID document fields from driver_profiles table."""
    op.drop_column('driver_profiles', 'id_verification_status')
    op.drop_column('driver_profiles', 'id_document_uploaded_at')
    op.drop_column('driver_profiles', 'id_document_type')
    op.drop_column('driver_profiles', 'id_document_path')
