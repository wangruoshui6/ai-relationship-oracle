from __future__ import annotations

from enum import Enum

from sqlalchemy import Boolean, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base, TimestampMixin
from app.utils.ids import generate_uuid


class KnowledgeDomain(str, Enum):
    TAROT = "tarot"
    BAZI = "bazi"
    PSYCHOLOGY = "psychology"


class KnowledgeDocument(TimestampMixin, Base):
    """RAG 知识库条目。

    一条记录 = 一个知识域（塔罗/八字/心理学）下的一个最小知识单元。
    塔罗场景：一张牌 × 一个方向（正位/逆位）为一条，共 78*2 = 156 条。
    向量检索的 embedding 结果存于外部索引，表中仅保留 embedding_id 关联。
    """

    __tablename__ = "knowledge_documents"
    __table_args__ = (
        UniqueConstraint("domain", "doc_key", name="uq_knowledge_domain_doc_key"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    domain: Mapped[str] = mapped_column(String(32), index=True, nullable=False)
    doc_key: Mapped[str] = mapped_column(String(128), nullable=False)
    title_zh: Mapped[str | None] = mapped_column(String(255), nullable=True)
    title_en: Mapped[str | None] = mapped_column(String(255), nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    keywords: Mapped[list | None] = mapped_column(JSON, nullable=True)
    meta: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    orientation: Mapped[str | None] = mapped_column(String(16), index=True, nullable=True)
    language: Mapped[str] = mapped_column(String(16), default="zh", nullable=False)
    source: Mapped[str | None] = mapped_column(String(255), nullable=True)
    license: Mapped[str | None] = mapped_column(String(64), nullable=True)
    embedding_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
