"""RAG 知识检索器与塔罗引擎接入测试。"""
from app.rag.retriever import KnowledgeRetriever, normalize_card_slug
from app.services.tarot_engine_service import TarotEngineService
from app.tools.result_schema import StructuredResult, ToolResult


class TestKnowledgeRetriever:
    def test_normalize_card_slug(self):
        assert normalize_card_slug("The Lovers") == "the-lovers"
        assert normalize_card_slug("The High Priestess") == "the-high-priestess"
        assert normalize_card_slug(" Wheel of Fortune ") == "wheel-of-fortune"

    def test_retrieve_tarot_card_upright(self):
        docs = KnowledgeRetriever().retrieve_tarot_card("The Lovers", "upright")
        assert len(docs) == 1
        assert docs[0].doc_key == "the-lovers__upright"
        assert "恋人" in (docs[0].title_zh or "")

    def test_retrieve_tarot_card_without_orientation(self):
        docs = KnowledgeRetriever().retrieve_tarot_card("The Lovers")
        assert len(docs) >= 2  # 正逆位均返回

    def test_retrieve_unknown_card_returns_empty(self):
        assert KnowledgeRetriever().retrieve_tarot_card("Not A Card", "upright") == []

    def test_keyword_search(self):
        docs = KnowledgeRetriever().search("tarot", "恋人")
        assert docs

    def test_build_rag_context(self):
        retriever = KnowledgeRetriever()
        docs = retriever.retrieve_tarot_card("The Lovers", "upright")
        ctx = retriever.build_rag_context(docs)
        assert "恋人" in ctx
        assert "来源" in ctx  # 来源标注


class TestTarotEngineRAG:
    def test_degraded_falls_back_to_knowledge_base(self, monkeypatch):
        engine = TarotEngineService()

        def boom(*args, **kwargs):
            raise RuntimeError("llm unavailable")

        monkeypatch.setattr(engine.llm, "generate_text", boom)
        result = engine.analyze({})
        assert result.status == "degraded"
        assert "symbolic" in result.confidence_notes.lower()
        # 降级时使用知识库牌意兜底（含来源标注），而不是空/硬编码
        assert "来源" in result.confidence_notes

    def test_prompt_includes_grounding(self, monkeypatch):
        engine = TarotEngineService()
        captured = {}

        def fake_generate(system_prompt, prompt):
            captured["prompt"] = prompt
            return '{"card_name": "The Lovers", "card_meaning": "deep union", "core_signals": ["union"]}'

        monkeypatch.setattr(engine.llm, "generate_text", fake_generate)
        result = engine.analyze({"user_message": "will we reconcile?"})
        assert result.status == "ok"
        assert "Reference knowledge base entry" in captured["prompt"]


class TestConsultationRAGContext:
    def test_build_rag_context_from_tarot_signal(self):
        from app.services.consultation_service import ConsultationService

        tr = ToolResult(tool="tarot", status="ok", core_signals=["card: The Lovers (upright)"])
        sr = StructuredResult(tool_results=[tr])
        cs = ConsultationService.__new__(ConsultationService)
        ctx = cs._build_rag_context(sr)
        assert ctx is not None
        assert "恋人" in ctx

    def test_build_rag_context_none_without_tarot(self):
        from app.services.consultation_service import ConsultationService

        sr = StructuredResult(tool_results=[ToolResult(tool="bazi", status="ok")])
        cs = ConsultationService.__new__(ConsultationService)
        assert cs._build_rag_context(sr) is None

    def test_build_rag_context_includes_bazi(self):
        from app.services.consultation_service import ConsultationService

        tr = ToolResult(
            tool="bazi", status="ok",
            core_signals=["day master: 甲(木)", "zodiac: rat", "dominant element: 火 (3 of 8)"],
        )
        sr = StructuredResult(tool_results=[tr])
        cs = ConsultationService.__new__(ConsultationService)
        ctx = cs._build_rag_context(sr)
        assert ctx is not None
        assert "Bazi Grounding" in ctx

    def test_build_rag_context_includes_psychology(self):
        from app.services.consultation_service import ConsultationService

        tr = ToolResult(
            tool="psychology", status="ok",
            core_signals=["anxious attachment visible"],
            confidence_notes="Attachment style: anxious. Communication: demand-withdraw.",
        )
        sr = StructuredResult(tool_results=[tr])
        cs = ConsultationService.__new__(ConsultationService)
        ctx = cs._build_rag_context(sr)
        assert ctx is not None
        assert "Psychology Grounding" in ctx

    def test_build_rag_context_all_domains(self):
        from app.services.consultation_service import ConsultationService

        sr = StructuredResult(tool_results=[
            ToolResult(tool="tarot", status="ok", core_signals=["card: The Lovers (upright)"]),
            ToolResult(tool="bazi", status="ok", core_signals=["zodiac: rat", "strong earth: stable"]),
            ToolResult(
                tool="psychology", status="ok",
                core_signals=["secure attachment"],
                confidence_notes="Attachment style: secure. Communication: n/a.",
            ),
        ])
        cs = ConsultationService.__new__(ConsultationService)
        ctx = cs._build_rag_context(sr)
        assert ctx
        for mark in ("Tarot Grounding", "Bazi Grounding", "Psychology Grounding"):
            assert mark in ctx

    def test_bazi_degraded_still_falls_back_to_knowledge(self):
        from app.services.consultation_service import ConsultationService

        tr = ToolResult(
            tool="bazi", status="degraded",
            core_signals=["insufficient birth data"],
            confidence_notes="Cannot compute Bazi chart without birth date.",
        )
        sr = StructuredResult(tool_results=[tr])
        cs = ConsultationService.__new__(ConsultationService)
        # 引擎降级时仍用"合婚"兜底检索，保证 LLM 有参考依据
        ctx = cs._build_rag_context(sr)
        assert ctx is not None
        assert "Bazi Grounding" in ctx
