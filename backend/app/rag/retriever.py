"""RAG 知识检索器。

从 knowledge_documents 表检索知识条目，供咨询流程注入 rag_context。

当前实现：
- 塔罗牌精确检索：按「牌名 slug + 正逆位」查库（doc_key 形如 the-lovers__upright）
- 通用关键词检索：content / title 模糊匹配
- 向量检索（embedding）：预留 search_vector 接口，后续接入 sqlite-vec / FAISS

设计约束：检索本身不调用 LLM（与 docs/04 的 RAG 链路一致），结果只做依据注入。
"""

from __future__ import annotations

from sqlalchemy import or_, select

from app.db.session import SessionLocal
from app.models.knowledge_document import KnowledgeDocument, KnowledgeDomain


def normalize_card_slug(name_en: str) -> str:
    """'The Lovers' -> 'the-lovers'（与 love-tarot.json 的 slug 命名一致）。"""
    return name_en.strip().lower().replace(" ", "-")


class KnowledgeRetriever:
    """知识库检索器。每个方法内部使用独立 session，无状态泄漏。"""

    def close(self) -> None:
        """兼容持有式调用。当前实现为无状态（session 方法内自管理），无需清理。"""

    def retrieve_tarot_card(
        self,
        card_name_en: str,
        orientation: str | None = None,
    ) -> list[KnowledgeDocument]:
        """按英文牌名 + 方向检索塔罗条目。

        - 方向已知时优先精确匹配 doc_key（如 the-lovers__upright）；
        - 未命中或方向未知时按 title_en 前缀兜底，返回该牌全部方向条目。
        """
        session = SessionLocal()
        try:
            slug = normalize_card_slug(card_name_en)
            if orientation:
                doc = session.scalar(
                    select(KnowledgeDocument).where(
                        KnowledgeDocument.domain == KnowledgeDomain.TAROT.value,
                        KnowledgeDocument.doc_key == f"{slug}__{orientation}",
                        KnowledgeDocument.is_active.is_(True),
                    )
                )
                if doc is not None:
                    return [doc]

            prefix = f"{card_name_en.strip()} ·"
            docs = session.scalars(
                select(KnowledgeDocument)
                .where(
                    KnowledgeDocument.domain == KnowledgeDomain.TAROT.value,
                    KnowledgeDocument.title_en.like(f"{prefix}%"),
                    KnowledgeDocument.is_active.is_(True),
                )
                .order_by(KnowledgeDocument.doc_key)
            ).all()
            return list(docs)
        finally:
            session.close()

    def search(self, domain: str, query: str, limit: int = 5) -> list[KnowledgeDocument]:
        """按关键词模糊检索（content / title_zh / title_en）。"""
        session = SessionLocal()
        try:
            like = f"%{query}%"
            docs = session.scalars(
                select(KnowledgeDocument)
                .where(
                    KnowledgeDocument.domain == domain,
                    KnowledgeDocument.is_active.is_(True),
                    or_(
                        KnowledgeDocument.content.like(like),
                        KnowledgeDocument.title_zh.like(like),
                        KnowledgeDocument.title_en.like(like),
                    ),
                )
                .limit(limit)
            ).all()
            return list(docs)
        finally:
            session.close()

    def search_vector(self, domain: str, query: str, limit: int = 5) -> list[KnowledgeDocument]:
        """向量检索预留接口：语料规模扩大或 embedding 接入后实现。"""
        # 当前语料规模（156 条塔罗）下关键词检索已足够；此接口保持签名兼容。
        return self.search(domain, query, limit)

    def build_rag_context(self, docs: list[KnowledgeDocument]) -> str:
        """把知识条目格式化为 prompt 可注入的文本（含来源标注）。"""
        if not docs:
            return ""
        lines: list[str] = []
        for doc in docs:
            title = doc.title_zh or doc.title_en or doc.doc_key
            source = f"（来源：{doc.source}）" if doc.source else ""
            lines.append(f"- {title}：{doc.content}{source}")
        return "\n".join(lines)
