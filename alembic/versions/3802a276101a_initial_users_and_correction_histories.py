"""initial: users and correction_histories

Revision ID: 3802a276101a
Revises:
Create Date: 2026-02-28 10:15:45.284844

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3802a276101a'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'users',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('nickname', sa.String(100), nullable=False),
        sa.Column('profile_image', sa.String(500), nullable=True),
        sa.Column('provider', sa.String(20), nullable=False),
        sa.Column('provider_id', sa.String(255), nullable=False),
        sa.Column('refresh_token', sa.String(500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('provider', 'provider_id', name='uq_provider_provider_id'),
    )

    op.create_table(
        'correction_histories',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('user_id', sa.Uuid(), nullable=False),
        sa.Column('original_comment', sa.Text(), nullable=False),
        sa.Column('corrected_comment', sa.Text(), nullable=False),
        sa.Column('is_corrected', sa.Boolean(), nullable=False),
        sa.Column('severity', sa.String(10), nullable=True),
        sa.Column('confidence', sa.Float(), nullable=True),
        sa.Column('problem_types', sa.JSON(), nullable=True),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_correction_histories_user_id', 'correction_histories', ['user_id'])
    op.create_index('ix_correction_histories_created_at', 'correction_histories', ['created_at'])


def downgrade() -> None:
    op.drop_index('ix_correction_histories_created_at', 'correction_histories')
    op.drop_index('ix_correction_histories_user_id', 'correction_histories')
    op.drop_table('correction_histories')
    op.drop_table('users')
