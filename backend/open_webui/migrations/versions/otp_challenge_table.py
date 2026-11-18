"""add persistent email OTP challenges

Revision ID: otp_challenge_table
Revises: 0bd252b206fb
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = 'otp_challenge_table'
down_revision: str | None = '0bd252b206fb'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        'otp_challenge',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('code_hash', sa.String(), nullable=False),
        sa.Column('created_at', sa.Integer(), nullable=False),
        sa.Column('expires_at', sa.Integer(), nullable=False),
        sa.Column('attempts', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('consumed', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('id'),
    )
    op.create_index('ix_otp_challenge_email', 'otp_challenge', ['email'])


def downgrade() -> None:
    op.drop_index('ix_otp_challenge_email', table_name='otp_challenge')
    op.drop_table('otp_challenge')
