"""Week 6 tests: PsychologyEngineService."""
import pytest
from app.services.psychology_engine_service import PsychologyEngineService
from app.tools.result_schema import ToolResult


class TestPsychologyEngine:
    def test_breakup_status_generates_grief_signals(self):
        engine = PsychologyEngineService()
        result = engine.analyze({"current_status": "breakup"})
        assert isinstance(result, ToolResult)
        assert "grief processing" in result.core_signals
        assert len(result.actions) > 0

    def test_conflict_status_generates_conflict_signals(self):
        engine = PsychologyEngineService()
        result = engine.analyze({"current_status": "conflict"})
        assert "avoidant tendencies" in result.core_signals or any("avoidant" in s for s in result.core_signals)

    def test_unknown_status_uses_default(self):
        engine = PsychologyEngineService()
        result = engine.analyze({})
        assert result.tool == "psychology"
        assert result.status == "ok"
        assert result.core_signals

    def test_enriches_with_additional_data(self):
        engine = PsychologyEngineService()
        result = engine.analyze({
            "current_status": "breakup",
            "conflict_level": "high",
            "trust_level": "low"
        })
        assert any("conflict level" in s for s in result.core_signals)
        assert any("trust level" in s for s in result.core_signals)
