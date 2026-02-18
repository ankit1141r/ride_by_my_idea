"""Create rating model

Revision ID: 005
Revises: 004
Create Date: 2026-02-18

"""
from alembic import op
import sqlalchemy as sa


revision = '005'
down_revision = '004'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('ratings',
        sa.Column('rating_id', sa.String(length=36), nullable=False),
        sa.Column('ride_id', sa.String(length=36), nullable=False),
        sa.Column('rater_id', sa.String(length=36), nullable=False),
        sa.Column('ratee_id', sa.String(length=36), nullable=False),
        sa.Column('stars', sa.Integer(), nullable=False),
        sa.Column('review', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.CheckConstraint('stars >= 1 AND stars <= 5', name='check_stars_range'),
        sa.ForeignKeyConstraint(['ride_id'], ['rides.ride_id'], ),
        sa.ForeignKeyConstraint(['rater_id'], ['users.user_id'], ),
        sa.ForeignKeyConstraint(['ratee_id'], ['users.user_id'], ),
        sa.PrimaryKeyConstraint('rating_id')
    )
    
    op.create_index(op.f('ix_ratings_ride_id'), 'ratings', ['ride_id'], unique=False)
    op.create_index(op.f('ix_ratings_rater_id'), 'ratings', ['rater_id'], unique=False)
    op.create_index(op.f('ix_ratings_ratee_id'), 'ratings', ['ratee_id'], unique=False)
    op.create_index(op.f('ix_ratings_created_at'), 'ratings', ['created_at'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_ratings_created_at'), table_name='ratings')
    op.drop_index(op.f('ix_ratings_ratee_id'), table_name='ratings')
    op.drop_index(op.f('ix_ratings_rater_id'), table_name='ratings')
    op.drop_index(op.f('ix_ratings_ride_id'), table_name='ratings')
    op.drop_table('ratings')
