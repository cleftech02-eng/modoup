
"""initial database setup

Revision ID: ee49962129b2
Revises: f03afeaa1200
Create Date: 2026-11-20 06:02:54.090933

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# Revision identifiers
revision: str = 'ee49962129b2'
down_revision: Union[str, None] = 'f03afeaa1200'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



def upgrade() -> None:
    op.create_table(
        'auth_attempts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('action', sa.String(length=30), nullable=False),
        sa.Column('identifier', sa.String(length=64), nullable=False),
        sa.Column('attempts', sa.Integer(), nullable=False),
        sa.Column('window_started_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('blocked_until', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint(
            'action',
            'identifier',
            name='uq_auth_attempt_action_identifier'
        )
    )

    op.create_index(
        op.f('ix_auth_attempts_id'),
        'auth_attempts',
        ['id'],
        unique=False
    )

    op.create_index(
        op.f('ix_auth_attempts_identifier'),
        'auth_attempts',
        ['identifier'],
        unique=False
    )

    # Add verification column.
    # Existing users will receive True.
    op.add_column(
        'users',
        sa.Column(
            'is_verified',
            sa.Boolean(),
            server_default=sa.true(),
            nullable=False
        )
    )

    op.alter_column(
        'users',
        'is_verified',
        server_default=None
    )

    # Add Google authentication ID.
    op.add_column(
        'users',
        sa.Column('google_id', sa.String(length=255), nullable=True)
    )

    # Existing accounts are local accounts.
    op.add_column(
        'users',
        sa.Column(
            'auth_provider',
            sa.String(length=20),
            server_default='local',
            nullable=False
        )
    )

    op.alter_column(
        'users',
        'auth_provider',
        server_default=None
    )

    # Allow Google users to have no password.
    op.alter_column(
        'users',
        'password_hash',
        existing_type=sa.VARCHAR(length=255),
        nullable=True
    )

    # Give the Google ID constraint an explicit name.
    op.create_unique_constraint(
        'uq_users_google_id',
        'users',
        ['google_id']
    )

def downgrade() -> None:
    op.drop_constraint(
        'uq_users_google_id',
        'users',
        type_='unique'
    )

    op.alter_column(
        'users',
        'password_hash',
        existing_type=sa.VARCHAR(length=255),
        nullable=False
    )

    op.drop_column('users', 'auth_provider')
    op.drop_column('users', 'google_id')
    op.drop_column('users', 'is_verified')

    op.drop_index(
        op.f('ix_auth_attempts_identifier'),
        table_name='auth_attempts'
    )

    op.drop_index(
        op.f('ix_auth_attempts_id'),
        table_name='auth_attempts'
    )

    op.drop_table('auth_attempts')
