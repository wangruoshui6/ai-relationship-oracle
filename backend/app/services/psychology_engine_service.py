"""LLM-driven Psychology Engine — analyzes attachment styles, communication patterns, MBTI."""
import json
from app.tools.base import BaseTool
from app.tools.result_schema import ToolResult
from app.services.llm_provider_service import LLMProviderService


PSYCHOLOGY_SYSTEM_PROMPT = """You are a relationship psychology analyst. Based on the user's question and relationship context, provide a structured psychological analysis.

Output MUST be valid JSON with these exact keys:
{
  "attachment_style": "most likely attachment style (secure/anxious/avoidant/fearful-avoidant) based on context",
  "communication_pattern": "identified communication pattern",
  "core_signals": ["3-5 key psychological observations"],
  "risks": ["2-3 psychological risks or red flags"],
  "opportunities": ["2-3 growth opportunities"],
  "actions": ["2-3 concrete, actionable psychological strategies"]
}

Rules:
- Infer attachment style from the user's language and behaviors described.
- Reference attachment theory, Gottman's communication patterns, or MBTI if relevant.
- Be specific to THIS situation, not generic.
- Use psychological terminology naturally but make it understandable.
- All array values must be strings.
"""


class PsychologyEngineService(BaseTool):
    tool_name = "psychology"

    def __init__(self) -> None:
        self.llm = LLMProviderService()

    def analyze(self, data: dict) -> ToolResult:
        user_message = data.get("user_message", "")
        current_status = data.get("current_status", "unknown")
        conflict_level = data.get("conflict_level", "")
        trust_level = data.get("trust_level", "")
        intimacy_level = data.get("intimacy_level", "")

        context = f"""User's question: {user_message}

Relationship context:
- Status: {current_status}
- Conflict level: {conflict_level or 'unknown'}
- Trust level: {trust_level or 'unknown'}
- Intimacy level: {intimacy_level or 'unknown'}

Analyze the psychological dynamics and provide structured output."""

        try:
            raw = self.llm.generate_text(PSYCHOLOGY_SYSTEM_PROMPT, context)
            parsed = self._parse_json(raw)
            return ToolResult(
                tool=self.tool_name,
                status="ok",
                core_signals=parsed.get("core_signals", []),
                risks=parsed.get("risks", []),
                opportunities=parsed.get("opportunities", []),
                actions=parsed.get("actions", []),
                confidence_notes=f"Attachment style: {parsed.get('attachment_style', 'unknown')}. Communication: {parsed.get('communication_pattern', 'n/a')}.",
            )
        except Exception:
            return ToolResult(
                tool=self.tool_name,
                status="degraded",
                core_signals=["analysis unavailable"],
                risks=[],
                opportunities=[],
                actions=["Try again or provide more context about your relationship dynamic"],
                confidence_notes="Psychology analysis failed. Falling back to general guidance.",
            )

    @staticmethod
    def _parse_json(raw: str) -> dict:
        raw = raw.strip()
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[-1]
            if raw.endswith("```"):
                raw = raw[:-3]
            raw = raw.strip()
        return json.loads(raw)
