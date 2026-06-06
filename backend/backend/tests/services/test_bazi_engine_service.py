"""Week 6 tests: BaziEngineService."""
import pytest
from app.services.bazi_engine_service import BaziEngineService
from app.tools.result_schema import ToolResult


class TestBaziEngine:
    def test_no_bazi_data_returns_degraded(self):
        engine = BaziEngineService()
        result = engine.analyze({})
        assert result.status == "degraded"
        assert "insufficient birth data" in result.core_signals

    def test_with_bazi_chart_returns_analysis(self):
        engine = BaziEngineService()
        result = engine.analyze({
            "bazi_chart": {
                "pillars": [
                    {"pillar": "年", "stem": "戊", "branch": "寅", "stem_element": "土", "branch_element": "木"},
                    {"pillar": "月", "stem": "丙", "branch": "辰", "stem_element": "火", "branch_element": "土"},
                    {"pillar": "日", "stem": "戊", "branch": "申", "stem_element": "土", "branch_element": "金"},
                    {"pillar": "时", "stem": "庚", "branch": "申", "stem_element": "金", "branch_element": "金"},
                ],
                "day_master": "戊",
                "day_master_element": "土",
                "zodiac": "虎",
                "has_birth_time": True
            },
            "five_elements": {"counts": {"木": 1, "火": 1, "土": 3, "金": 3, "水": 0}}
        })
        assert result.status == "ok"
        assert any("day master" in s for s in result.core_signals)

    def test_zodiac_harmony_detected(self):
        engine = BaziEngineService()
        result = engine.analyze({
            "bazi_chart": {
                "pillars": [{"pillar": "年", "stem": "甲", "branch": "子", "stem_element": "木", "branch_element": "水"}],
                "day_master": "甲",
                "day_master_element": "木",
                "zodiac": "鼠",
                "has_birth_time": True
            },
            "partner_zodiac": "龙"
        })
        assert any("harmony" in s for s in result.core_signals)

    def test_zodiac_clash_detected(self):
        engine = BaziEngineService()
        result = engine.analyze({
            "bazi_chart": {
                "pillars": [{"pillar": "年", "stem": "甲", "branch": "子", "stem_element": "木", "branch_element": "水"}],
                "day_master": "甲",
                "day_master_element": "木",
                "zodiac": "鼠",
                "has_birth_time": True
            },
            "partner_zodiac": "马"
        })
        assert any("clash" in s for s in result.core_signals)
