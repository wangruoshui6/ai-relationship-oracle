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

    def test_partner_full_chart_generates_pair_analysis_signals(self):
        engine = BaziEngineService()
        result = engine.analyze({
            "bazi_chart": {
                "pillars": [
                    {"pillar": "年", "stem": "乙", "branch": "酉", "stem_element": "木", "branch_element": "金"},
                    {"pillar": "月", "stem": "甲", "branch": "申", "stem_element": "木", "branch_element": "金"},
                    {"pillar": "日", "stem": "丁", "branch": "亥", "stem_element": "火", "branch_element": "水"},
                    {"pillar": "时", "stem": "癸", "branch": "巳", "stem_element": "水", "branch_element": "火"},
                ],
                "day_master": "丁",
                "day_master_element": "火",
                "zodiac": "鸡",
                "has_birth_time": True
            },
            "five_elements": {"counts": {"木": 2, "火": 2, "土": 0, "金": 2, "水": 2}},
            "partner_bazi_chart": {
                "pillars": [
                    {"pillar": "年", "stem": "丁", "branch": "亥", "stem_element": "火", "branch_element": "水"},
                    {"pillar": "月", "stem": "壬", "branch": "寅", "stem_element": "水", "branch_element": "木"},
                    {"pillar": "日", "stem": "己", "branch": "卯", "stem_element": "土", "branch_element": "木"},
                    {"pillar": "时", "stem": "乙", "branch": "丑", "stem_element": "木", "branch_element": "土"},
                ],
                "day_master": "己",
                "day_master_element": "土",
                "zodiac": "猪",
                "has_birth_time": True
            }
        })

        assert result.status == "ok"
        assert any("partner day master" in s for s in result.core_signals)
        assert any("day master relation" in s for s in result.core_signals)
        assert any("partner dominant element" in s for s in result.core_signals)
        assert any("Partner Bazi:" in a for a in result.actions)

    def test_partner_missing_birth_time_reduces_confidence(self):
        engine = BaziEngineService()
        result = engine.analyze({
            "bazi_chart": {
                "pillars": [
                    {"pillar": "年", "stem": "甲", "branch": "子", "stem_element": "木", "branch_element": "水"},
                    {"pillar": "月", "stem": "丙", "branch": "寅", "stem_element": "火", "branch_element": "木"},
                    {"pillar": "日", "stem": "甲", "branch": "辰", "stem_element": "木", "branch_element": "土"},
                ],
                "day_master": "甲",
                "day_master_element": "木",
                "zodiac": "鼠",
                "has_birth_time": True
            },
            "partner_bazi_chart": {
                "pillars": [
                    {"pillar": "年", "stem": "己", "branch": "丑", "stem_element": "土", "branch_element": "土"},
                    {"pillar": "月", "stem": "辛", "branch": "卯", "stem_element": "金", "branch_element": "木"},
                    {"pillar": "日", "stem": "癸", "branch": "酉", "stem_element": "水", "branch_element": "金"},
                ],
                "day_master": "癸",
                "day_master_element": "水",
                "zodiac": "牛",
                "has_birth_time": False
            }
        })

        assert result.status == "ok"
        assert result.confidence_notes is not None
        assert "Partner birth time is missing" in result.confidence_notes
