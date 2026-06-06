"""Compatibility Engine Service — cross-dimension relationship synthesis.

Fuses Bazi, Psychology, and Tarot results into a unified compatibility analysis
using LLM-powered cross-referencing.
"""
import json
from app.tools.result_schema import ToolResult
from app.services.llm_provider_service import LLMProviderService
from app.services.prompt_center_service import get_prompt_center


class CompatibilityEngineService:
    """Synthesizes multi-dimensional analysis results into unified insights."""

    DEFAULT_COMPATIBILITY_PROMPT = (
        "You synthesize Bazi, psychology, and tarot results into a grounded "
        "relationship compatibility summary. Return compact JSON with keys: "
        "overall_compatibility, cross_analysis, overall_risks, "
        "overall_opportunities, recommendations."
    )

    def __init__(self) -> None:
        self.llm = LLMProviderService()
        self.prompt_center = get_prompt_center()

    def synthesize(
        self,
        bazi_result: ToolResult | None,
        psychology_result: ToolResult | None,
        tarot_result: ToolResult | None,
        relationship_context: dict | None = None,
    ) -> ToolResult:
        """Fuse all tool results into a unified compatibility analysis."""

        # Build context for the LLM
        context_parts = ["Synthesize the following relationship analysis results:\n"]

        if bazi_result and bazi_result.status != "degraded":
            context_parts.append(f"Bazi Analysis: {json.dumps(self._result_to_dict(bazi_result), ensure_ascii=False)}")
        else:
            context_parts.append("Bazi Analysis: Not available (insufficient birth data)")

        if psychology_result:
            context_parts.append(f"Psychology Analysis: {json.dumps(self._result_to_dict(psychology_result), ensure_ascii=False)}")
        else:
            context_parts.append("Psychology Analysis: Not available")

        if tarot_result:
            context_parts.append(f"Tarot Analysis: {json.dumps(self._result_to_dict(tarot_result), ensure_ascii=False)}")
        else:
            context_parts.append("Tarot Analysis: Not available")

        if relationship_context:
            ctx_str = json.dumps(
                self._serialize_relationship_context(relationship_context),
                ensure_ascii=False,
            )
            context_parts.append(f"Relationship Context: {ctx_str}")

        context = "\n".join(context_parts)

        try:
            system_prompt = self.prompt_center.get_or_default(
                "compatibility",
                self.DEFAULT_COMPATIBILITY_PROMPT,
            )
            raw = self.llm.generate_text(system_prompt, context)
            parsed = self._parse_json(raw)
            if not parsed:
                raise ValueError("empty compatibility json")

            return ToolResult(
                tool="compatibility",
                status="ok",
                core_signals=parsed.get("cross_analysis", []),
                risks=parsed.get("overall_risks", []),
                opportunities=parsed.get("overall_opportunities", []),
                actions=parsed.get("recommendations", []),
                confidence_notes=f"Overall: {parsed.get('overall_compatibility', '')}",
            )
        except Exception:
            return ToolResult(
                tool="compatibility",
                status="degraded",
                core_signals=["compatibility synthesis unavailable"],
                risks=[],
                opportunities=[],
                actions=["Individual tool results are still available for review"],
                confidence_notes="Cross-dimension synthesis failed. Review individual analyses separately.",
            )

    @staticmethod
    def _result_to_dict(r: ToolResult) -> dict:
        return {
            "tool": r.tool,
            "status": r.status,
            "core_signals": r.core_signals,
            "risks": r.risks,
            "opportunities": r.opportunities,
            "actions": r.actions,
        }

    @staticmethod
    def _serialize_relationship_context(context: dict | None) -> dict:
        if not context:
            return {}

        profile = context.get("profile")
        summary = context.get("summary")
        recent_events = context.get("recent_events") or []

        serialized: dict = {
            "profile": None,
            "summary": None,
            "recent_events": [],
        }

        if profile is not None:
            serialized["profile"] = {
                "current_status": getattr(profile, "current_status", None),
                "current_goal": getattr(profile, "current_goal", None),
                "relationship_stage": getattr(profile, "relationship_stage", None),
                "trust_level": getattr(profile, "trust_level", None),
                "conflict_level": getattr(profile, "conflict_level", None),
                "intimacy_level": getattr(profile, "intimacy_level", None),
                "summary_snapshot": getattr(profile, "summary_snapshot", None),
            }

        if summary is not None:
            serialized["summary"] = {
                "summary": getattr(summary, "summary", None),
                "summary_version": getattr(summary, "summary_version", None),
            }

        for event in recent_events:
            serialized["recent_events"].append(
                {
                    "event_type": getattr(event, "event_type", None),
                    "event_date": str(getattr(event, "event_date", None))
                    if getattr(event, "event_date", None)
                    else None,
                    "description": getattr(event, "description", None),
                    "confidence_score": getattr(event, "confidence_score", None),
                }
            )

        return serialized

    @staticmethod
    def _parse_json(raw: str) -> dict:
        if not raw:
            return {}
        raw = raw.strip()
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[-1]
            if raw.rstrip().endswith("```"):
                raw = raw.rsplit("```", 1)[0]
        try:
            return json.loads(raw.strip())
        except json.JSONDecodeError:
            return {}
