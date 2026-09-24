"""create knowledge_documents table

Revision ID: 20260924_0008
Revises: 20260605_0007
Create Date: 2026-09-24 10:00:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260924_0008"
down_revision = "20260605_0007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "knowledge_documents",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("domain", sa.String(length=32), nullable=False),
        sa.Column("doc_key", sa.String(length=128), nullable=False),
        sa.Column("title_zh", sa.String(length=255), nullable=True),
        sa.Column("title_en", sa.String(length=255), nullable=True),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("keywords", sa.JSON(), nullable=True),
        sa.Column("meta", sa.JSON(), nullable=True),
        sa.Column("orientation", sa.String(length=16), nullable=True),
        sa.Column("language", sa.String(length=16), nullable=False),
        sa.Column("source", sa.String(length=255), nullable=True),
        sa.Column("license", sa.String(length=64), nullable=True),
        sa.Column("embedding_id", sa.String(length=64), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("domain", "doc_key", name="uq_knowledge_domain_doc_key"),
    )
    op.create_index(op.f("ix_knowledge_documents_domain"), "knowledge_documents", ["domain"], unique=False)
    op.create_index(op.f("ix_knowledge_documents_orientation"), "knowledge_documents", ["orientation"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_knowledge_documents_orientation"), table_name="knowledge_documents")
    op.drop_index(op.f("ix_knowledge_documents_domain"), table_name="knowledge_documents")
    op.drop_table("knowledge_documents")
