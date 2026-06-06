"""create user_profile and partner_profile tables

Revision ID: 20260604_0002
Revises: 20260604_0001
Create Date: 2026-06-04 00:30:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260604_0002"
down_revision = "20260604_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "user_profile",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column(
            "gender",
            sa.Enum("male", "female", "other", "unknown", name="genderenum", native_enum=False),
            nullable=True,
        ),
        sa.Column("birth_date", sa.Date(), nullable=True),
        sa.Column("birth_time", sa.Time(), nullable=True),
        sa.Column("birth_city", sa.String(length=255), nullable=True),
        sa.Column("birth_country", sa.String(length=255), nullable=True),
        sa.Column("bazi_chart", sa.JSON(), nullable=True),
        sa.Column("five_elements", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", name="uq_user_profile_user_id"),
    )
    op.create_index(op.f("ix_user_profile_user_id"), "user_profile", ["user_id"], unique=False)

    op.create_table(
        "partner_profile",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("nickname", sa.String(length=255), nullable=False),
        sa.Column(
            "gender",
            sa.Enum("male", "female", "other", "unknown", name="genderenum", native_enum=False),
            nullable=True,
        ),
        sa.Column(
            "relationship_type",
            sa.Enum(
                "ex",
                "current",
                "crush",
                "spouse",
                "friend",
                "unknown",
                name="relationshiptypeenum",
                native_enum=False,
            ),
            nullable=True,
        ),
        sa.Column("birth_date", sa.Date(), nullable=True),
        sa.Column("birth_time", sa.Time(), nullable=True),
        sa.Column("birth_city", sa.String(length=255), nullable=True),
        sa.Column("birth_country", sa.String(length=255), nullable=True),
        sa.Column("bazi_chart", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_partner_profile_user_id"), "partner_profile", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_partner_profile_user_id"), table_name="partner_profile")
    op.drop_table("partner_profile")
    op.drop_index(op.f("ix_user_profile_user_id"), table_name="user_profile")
    op.drop_table("user_profile")
