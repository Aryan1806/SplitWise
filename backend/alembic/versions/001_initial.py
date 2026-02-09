"""Initial migration - Create all tables

Revision ID: 001_initial
Revises: 
Create Date: 2024-02-10 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
import uuid

# revision identifiers, used by Alembic.
revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create all tables for SplitMint application."""
    
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('full_name', sa.String(255), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False)
    )
    # Create index on email for fast lookups
    op.create_index('ix_users_email', 'users', ['email'])
    op.create_index('ix_users_id', 'users', ['id'])
    
    # Create groups table
    op.create_table(
        'groups',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('owner_id', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False)
    )
    op.create_index('ix_groups_id', 'groups', ['id'])
    op.create_index('ix_groups_owner_id', 'groups', ['owner_id'])
    
    # Create participants table
    op.create_table(
        'participants',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('group_id', UUID(as_uuid=True), sa.ForeignKey('groups.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('color', sa.String(7), nullable=True),
        sa.Column('avatar_url', sa.String(500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False)
    )
    op.create_index('ix_participants_id', 'participants', ['id'])
    op.create_index('ix_participants_group_id', 'participants', ['group_id'])
    # Unique constraint: participant names must be unique within a group
    op.create_unique_constraint('uq_group_participant_name', 'participants', ['group_id', 'name'])
    
    # Create expenses table
    op.create_table(
        'expenses',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('group_id', UUID(as_uuid=True), sa.ForeignKey('groups.id', ondelete='CASCADE'), nullable=False),
        sa.Column('description', sa.String(500), nullable=False),
        sa.Column('amount', sa.Numeric(10, 2), nullable=False),
        sa.Column('payer_id', UUID(as_uuid=True), sa.ForeignKey('participants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('expense_date', sa.Date, nullable=False),
        sa.Column('split_mode', sa.String(20), nullable=False),
        sa.Column('category', sa.String(100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False)
    )
    op.create_index('ix_expenses_id', 'expenses', ['id'])
    op.create_index('ix_expenses_group_id', 'expenses', ['group_id'])
    op.create_index('ix_expenses_payer_id', 'expenses', ['payer_id'])
    op.create_index('ix_expenses_expense_date', 'expenses', ['expense_date'])
    op.create_index('ix_expenses_category', 'expenses', ['category'])
    
    # Create expense_splits table
    op.create_table(
        'expense_splits',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('expense_id', UUID(as_uuid=True), sa.ForeignKey('expenses.id', ondelete='CASCADE'), nullable=False),
        sa.Column('participant_id', UUID(as_uuid=True), sa.ForeignKey('participants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('amount', sa.Numeric(10, 2), nullable=False),
        sa.Column('percentage', sa.Numeric(5, 2), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False)
    )
    op.create_index('ix_expense_splits_id', 'expense_splits', ['id'])
    op.create_index('ix_expense_splits_expense_id', 'expense_splits', ['expense_id'])
    op.create_index('ix_expense_splits_participant_id', 'expense_splits', ['participant_id'])
    # Unique constraint: each participant appears only once per expense
    op.create_unique_constraint('uq_expense_participant', 'expense_splits', ['expense_id', 'participant_id'])


def downgrade() -> None:
    """Drop all tables."""
    # Drop tables in reverse order (respect foreign key constraints)
    op.drop_table('expense_splits')
    op.drop_table('expenses')
    op.drop_table('participants')
    op.drop_table('groups')
    op.drop_table('users')