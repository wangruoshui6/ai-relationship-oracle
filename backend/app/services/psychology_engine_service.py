"""LLM-driven Psychology Engine ? uses PromptCenter for prompt management."""
import json
from app.tools.base import BaseTool
from app.tools.result_schema import ToolResult
from app.services.llm_provider_service import LLMProviderService
from app.services.prompt_center_service import get_prompt_center


class PsychologyEngineService(BaseTool):
    tool_name = "psychology"
    DEFAULT_PSYCHOLOGY_PROMPT = (
        "You analyze relationship psychology. Return JSON with keys: "
        "core_signals, risks, opportunities, actions, attachment_style, "
        "communication_pattern."
    )

    def __init__(self) -> None:
        self.prompt_center = get_prompt_center()
        self.llm = LLMProviderService()

    def analyze(self, data: dict) -> ToolResult:
        user_message = data.get("user_message", "")
        current_status = data.get("current_status", "unknown")
        conflict_level = data.get("conflict_level", "")
        trust_level = data.get("trust_level", "")
        intimacy_level = data.get("intimacy_level", "")

        context = (
            f"User's question: {user_message}\n\n"
            f"Relationship context:\n"
            f"- Status: {current_status}\n"
            f"- Conflict level: {conflict_level or 'unknown'}\n"
            f"- Trust level: {trust_level or 'unknown'}\n"
            f"- Intimacy level: {intimacy_level or 'unknown'}\n\n"
            f"Analyze the psychological dynamics and provide structured output."
        )

        try:
            system_prompt = self.prompt_center.get_or_default(
                "psychology",
                self.DEFAULT_PSYCHOLOGY_PROMPT,
            )
            raw = self.llm.generate_text(system_prompt, context)
            parsed = self._parse_json(raw)
            if not parsed:
                raise ValueError("empty psychology json")
            return ToolResult(
                tool=self.tool_name, status="ok",
                core_signals=parsed.get("core_signals", []),
                risks=parsed.get("risks", []),
                opportunities=parsed.get("opportunities", []),
                actions=parsed.get("actions", []),
                confidence_notes=f"Attachment style: {parsed.get('attachment_style', 'unknown')}. Communication: {parsed.get('communication_pattern', 'n/a')}.",
            )
        except Exception:
            return ToolResult(
                tool=self.tool_name, status="degraded",
                core_signals=["analysis unavailable"], risks=[], opportunities=[],
                actions=["Try again or provide more context about your relationship dynamic"],
                confidence_notes="Psychology analysis failed. Falling back to general guidance.",
            )

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
