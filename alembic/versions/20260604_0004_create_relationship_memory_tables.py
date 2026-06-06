"""create relationship_profile and memory_summary tables

Revision ID: 20260604_0004
Revises: 20260604_0003
Create Date: 2026-06-04 02:00:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260604_0004"
down_revision = "20260604_0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "relationship_profile",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("partner_id", sa.String(length=36), nullable=False),
        sa.Column("current_status", sa.String(length=64), nullable=True),
        sa.Column("current_goal", sa.String(length=64), nullable=True),
        sa.Column("relationship_stage", sa.String(length=64), nullable=True),
        sa.Column("interaction_pattern", sa.String(length=128), nullable=True),
        sa.Column("trust_level", sa.String(length=64), nullable=True),
        sa.Column("conflict_level", sa.String(length=64), nullable=True),
        sa.Column("intimacy_level", sa.String(length=64), nullable=True),
        sa.Column("last_major_event", sa.String(length=128), nullable=True),
        sa.Column("summary_snapshot", sa.Text(), nullable=True),
        sa.Column("updated_by", sa.Enum("system", "user", name="updatedbyenum", native_enum=False), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["partner_id"], ["partner_profile.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "partner_id", name="uq_relationship_profile_user_partner"),
    )
    op.create_index(op.f("ix_relationship_profile_partner_id"), "relationship_profile", ["partner_id"], unique=False)
    op.create_index(op.f("ix_relationship_profile_user_id"), "relationship_profile", ["user_id"], unique=False)

    op.create_table(
        "memory_summary",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("partner_id", sa.String(length=36), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("summary_version", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["partner_id"], ["partner_profile.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "partner_id", name="uq_memory_summary_user_partner"),
    )
    op.create_index(op.f("ix_memory_summary_partner_id"), "memory_summary", ["partner_id"], unique=False)
    op.create_index(op.f("ix_memory_summary_user_id"), "memory_summary", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_memory_summary_user_id"), table_name="memory_summary")
    op.drop_index(op.f("ix_memory_summary_partner_id"), table_name="memory_summary")
    op.drop_table("memory_summary")
    op.drop_index(op.f("ix_relationship_profile_user_id"), table_name="relationship_profile")
    op.drop_index(op.f("ix_relationship_profile_partner_id"), table_name="relationship_profile")
    op.drop_table("relationship_profile")
