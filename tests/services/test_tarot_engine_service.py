"""Week 6 tests: TarotEngineService."""
import pytest
from app.services.tarot_engine_service import TarotEngineService
from app.tools.result_schema import ToolResult


class TestTarotEngine:
    def test_draw_returns_valid_result(self):
        engine = TarotEngineService()
        result = engine.analyze({})
        assert isinstance(result, ToolResult)
        assert result.tool == "tarot"
        assert result.status == "ok"
        assert result.core_signals
        assert "card:" in result.core_signals[0]

    def test_multiple_draws_generate_different_cards(self):
        engine = TarotEngineService()
        cards = set()
        for _ in range(20):
            result = engine.analyze({})
            cards.add(result.core_signals[0])
        # With 8 possible cards, 20 draws should yield at least 2 different
        assert len(cards) >= 2

    def test_has_confidence_notes(self):
        engine = TarotEngineService()
        result = engine.analyze({})
        assert result.confidence_notes is not None
        assert "symbolic" in result.confidence_notes.lower()
