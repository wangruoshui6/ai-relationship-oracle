"""add calendar fields to user_profile and partner_profile

Revision ID: 20260605_0005
Revises: f257560adef0
Create Date: 2026-06-05 12:00:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260605_0005"
down_revision = "f257560adef0"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "user_profile",
        sa.Column(
            "calendar_type",
            sa.Enum("solar", "lunar", name="calendartypeenum", native_enum=False),
            nullable=True,
        ),
    )
    op.add_column("user_profile", sa.Column("lunar_birth_date", sa.Date(), nullable=True))

    op.add_column(
        "partner_profile",
        sa.Column(
            "calendar_type",
            sa.Enum("solar", "lunar", name="calendartypeenum", native_enum=False),
            nullable=True,
        ),
    )
    op.add_column("partner_profile", sa.Column("lunar_birth_date", sa.Date(), nullable=True))


def downgrade() -> None:
    op.drop_column("partner_profile", "lunar_birth_date")
    op.drop_column("partner_profile", "calendar_type")
    op.drop_column("user_profile", "lunar_birth_date")
    op.drop_column("user_profile", "calendar_type")
