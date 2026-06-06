"""Week 6 tests: ToolRouterService."""
import pytest
from app.services.tool_router_service import ToolRouterService
from app.tools.result_schema import StructuredResult


class TestToolRouter:
    def test_validate_methods_defaults(self):
        router = ToolRouterService()
        result = router.validate_methods(None)
        assert result == ["bazi", "psychology"]

    def test_validate_methods_filters_invalid(self):
        router = ToolRouterService()
        result = router.validate_methods(["bazi", "invalid", "tarot"])
        assert result == ["bazi", "tarot"]

    def test_validate_methods_empty_list_uses_default(self):
        router = ToolRouterService()
        result = router.validate_methods([])
        assert result == ["bazi", "psychology"]

    def test_run_all_psychology(self):
        router = ToolRouterService()
        result = router.run_all(["psychology"], {"current_status": "breakup"})
        assert isinstance(result, StructuredResult)
        assert len(result.tool_results) == 1
        assert result.tool_results[0].tool == "psychology"

    def test_run_all_bazi_degraded(self):
        router = ToolRouterService()
        result = router.run_all(["bazi"], {})
        assert result.tool_results[0].status == "degraded"

    def test_run_all_multiple_tools(self):
        router = ToolRouterService()
        result = router.run_all(["bazi", "psychology", "tarot"], {})
        assert len(result.tool_results) == 3

    def test_summary_is_generated(self):
        router = ToolRouterService()
        result = router.run_all(["psychology"], {"current_status": "breakup"})
        assert result.summary
        assert len(result.summary) > 0
