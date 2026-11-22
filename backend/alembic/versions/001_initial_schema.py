"""Initial database schema migration

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-11-22 08:30:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. users
    op.create_table(
        'users',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('full_name', sa.String(255), nullable=False),
        sa.Column('avatar_url', sa.String(512), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('1')),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_users_email', 'users', ['email'], unique=True)
    op.create_index('ix_users_id', 'users', ['id'])

    # 2. destinations
    op.create_table(
        'destinations',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('state', sa.String(100), nullable=False),
        sa.Column('zone', sa.String(50), nullable=False),
        sa.Column('latitude', sa.Float(), nullable=False),
        sa.Column('longitude', sa.Float(), nullable=False),
        sa.Column('avg_cost_per_day', sa.Float(), nullable=False, server_default='2500.0'),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('tags', sa.JSON(), nullable=False),
    )
    op.create_index('ix_destinations_name', 'destinations', ['name'])
    op.create_index('ix_destinations_state', 'destinations', ['state'])

    # 3. attractions
    op.create_table(
        'attractions',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('place_id', sa.Integer(), nullable=False, unique=True),
        sa.Column('destination_id', sa.String(36), sa.ForeignKey('destinations.id', ondelete='SET NULL'), nullable=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('city', sa.String(100), nullable=False),
        sa.Column('state', sa.String(100), nullable=False),
        sa.Column('zone', sa.String(50), nullable=False),
        sa.Column('type', sa.String(100), nullable=False),
        sa.Column('rating', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('entrance_fee_inr', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('time_needed_hrs', sa.Float(), nullable=False, server_default='1.5'),
        sa.Column('reviews_lakhs', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('weekly_off', sa.String(50), nullable=False, server_default='Open All Days'),
        sa.Column('latitude', sa.Float(), nullable=False),
        sa.Column('longitude', sa.Float(), nullable=False),
        sa.Column('significance', sa.String(255), nullable=True),
        sa.Column('dslr_allowed', sa.Boolean(), nullable=False, server_default=sa.text('1')),
        sa.Column('best_time_to_visit', sa.String(100), nullable=False, server_default='All Day'),
        sa.Column('budget_tier', sa.String(50), nullable=False, server_default='Budget'),
        sa.Column('macro_category', sa.String(100), nullable=False, server_default='culture_heritage'),
        sa.Column('thematic_vectors', sa.JSON(), nullable=False),
    )
    op.create_index('ix_attractions_place_id', 'attractions', ['place_id'], unique=True)
    op.create_index('ix_attractions_name', 'attractions', ['name'])
    op.create_index('ix_attractions_city', 'attractions', ['city'])
    op.create_index('ix_attractions_state', 'attractions', ['state'])

    # 4. trips
    op.create_table(
        'trips',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('start_date', sa.Date(), nullable=True),
        sa.Column('end_date', sa.Date(), nullable=True),
        sa.Column('created_by', sa.String(36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('invite_code', sa.String(32), nullable=False, unique=True),
        sa.Column('status', sa.String(32), nullable=False, server_default='PLANNING'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_trips_invite_code', 'trips', ['invite_code'], unique=True)
    op.create_index('ix_trips_created_by', 'trips', ['created_by'])

    # 5. trip_members
    op.create_table(
        'trip_members',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('trip_id', sa.String(36), sa.ForeignKey('trips.id', ondelete='CASCADE'), nullable=False),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('role', sa.String(32), nullable=False, server_default='MEMBER'),
        sa.Column('joined_at', sa.DateTime(), nullable=False),
        sa.UniqueConstraint('trip_id', 'user_id', name='uq_trip_member'),
    )

    # 6. preferences
    op.create_table(
        'preferences',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('trip_id', sa.String(36), sa.ForeignKey('trips.id', ondelete='CASCADE'), nullable=False),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('budget_min', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('budget_max', sa.Float(), nullable=False, server_default='50000.0'),
        sa.Column('pace_preference', sa.String(32), nullable=False, server_default='MODERATE'),
        sa.Column('category_weights', sa.JSON(), nullable=False),
        sa.Column('dietary_restrictions', sa.String(255), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.UniqueConstraint('trip_id', 'user_id', name='uq_trip_user_preference'),
    )

    # 7. recommendations
    op.create_table(
        'recommendations',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('trip_id', sa.String(36), sa.ForeignKey('trips.id', ondelete='CASCADE'), nullable=False),
        sa.Column('attraction_id', sa.String(36), sa.ForeignKey('attractions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('group_score', sa.Float(), nullable=False),
        sa.Column('lowest_member_score', sa.Float(), nullable=False),
        sa.Column('agreement_index', sa.Float(), nullable=False, server_default='1.0'),
        sa.Column('rank', sa.Integer(), nullable=False),
        sa.Column('explanation_breakdown', sa.JSON(), nullable=False),
        sa.Column('generated_at', sa.DateTime(), nullable=False),
    )

    # 8. votes
    op.create_table(
        'votes',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('trip_id', sa.String(36), sa.ForeignKey('trips.id', ondelete='CASCADE'), nullable=False),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('target_type', sa.String(32), nullable=False, server_default='ATTRACTION'),
        sa.Column('target_id', sa.String(36), nullable=False),
        sa.Column('vote_value', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.UniqueConstraint('trip_id', 'user_id', 'target_type', 'target_id', name='uq_trip_vote'),
    )

    # 9. budget_items
    op.create_table(
        'budget_items',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('trip_id', sa.String(36), sa.ForeignKey('trips.id', ondelete='CASCADE'), nullable=False),
        sa.Column('created_by', sa.String(36), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('category', sa.String(100), nullable=False, server_default='Activities'),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('estimated_cost', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('actual_cost', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('split_method', sa.String(32), nullable=False, server_default='EQUAL'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )

    # 10. itinerary_days
    op.create_table(
        'itinerary_days',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('trip_id', sa.String(36), sa.ForeignKey('trips.id', ondelete='CASCADE'), nullable=False),
        sa.Column('day_number', sa.Integer(), nullable=False),
        sa.Column('date', sa.Date(), nullable=True),
    )

    # 11. itinerary_items
    op.create_table(
        'itinerary_items',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('itinerary_day_id', sa.String(36), sa.ForeignKey('itinerary_days.id', ondelete='CASCADE'), nullable=False),
        sa.Column('attraction_id', sa.String(36), sa.ForeignKey('attractions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('start_time', sa.String(10), nullable=True),
        sa.Column('end_time', sa.String(10), nullable=True),
        sa.Column('sort_order', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('notes', sa.Text(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table('itinerary_items')
    op.drop_table('itinerary_days')
    op.drop_table('budget_items')
    op.drop_table('votes')
    op.drop_table('recommendations')
    op.drop_table('preferences')
    op.drop_table('trip_members')
    op.drop_table('trips')
    op.drop_table('attractions')
    op.drop_table('destinations')
    op.drop_table('users')
