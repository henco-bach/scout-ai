"""add kickoff_offset_seconds and player name

Revision ID: b2e9f1a4d8c3
Revises: a1404614fc25
Create Date: 2026-07-10 22:40:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = "b2e9f1a4d8c3"
down_revision = "a1404614fc25"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "matches",
        sa.Column("kickoff_offset_seconds", sa.Float(), nullable=False, server_default="0.0"),
    )
    op.add_column("players", sa.Column("name", sa.String(length=128), nullable=True))


def downgrade() -> None:
    op.drop_column("players", "name")
    op.drop_column("matches", "kickoff_offset_seconds")
