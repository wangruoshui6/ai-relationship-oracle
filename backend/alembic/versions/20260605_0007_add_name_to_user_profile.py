"""add name column to user_profile

Revision ID: 20260605_0007
Revises: 20260605_0006
Create Date: 2026-06-05 16:00:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260605_0007"
down_revision = "20260605_0006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("user_profile", sa.Column("name", sa.String(length=255), nullable=True))


def downgrade() -> None:
    op.drop_column("user_profile", "name")
