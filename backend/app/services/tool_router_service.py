"""Week 6: Tool Router — dispatch to analysis engines based on methods."""
from app.tools.result_schema import ToolResult, StructuredResult
from app.services.bazi_engine_service import BaziEngineService
from app.services.psychology_engine_service import PsychologyEngineService
from app.services.tarot_engine_service import TarotEngineService


VALID_METHODS = {"bazi", "psychology", "tarot"}


class ToolRouterService:
    def __init__(self) -> None:
        self.engines = {
            "bazi": BaziEngineService(),
            "psychology": PsychologyEngineService(),
            "tarot": TarotEngineService(),
        }

    def validate_methods(self, methods: list[str] | None) -> list[str]:
        if not methods:
            return ["bazi", "psychology"]
        validated = [m for m in methods if m in VALID_METHODS]
        return validated if validated else ["bazi", "psychology"]

    def run_all(self, methods: list[str], data: dict) -> StructuredResult:
        results: list[ToolResult] = []
        for method in methods:
            engine = self.engines.get(method)
            if engine:
                result = engine.analyze(data)
                results.append(result)

        summary = self._build_summary(results)
        return StructuredResult(tool_results=results, summary=summary)

    @staticmethod
    def _build_summary(results: list[ToolResult]) -> str:
        if not results:
            return "No analysis available."
        parts = []
        for r in results:
            parts.append(f"[{r.tool}] {', '.join(r.core_signals[:3])}. Actions: {'; '.join(r.actions[:2])}.")
        return " ".join(parts)
