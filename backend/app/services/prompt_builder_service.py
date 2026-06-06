"""Prompt Builder Service — builds system + user prompts with memory and tool context."""
from app.core.constants import DEFAULT_ANALYSIS_METHODS
from app.tools.result_schema import StructuredResult


SYSTEM_BASE = """You are AI Relationship Oracle, an empathetic relationship advisor.
You help users understand their relationships through astrology (Bazi), psychology, and tarot.

Guidelines:
- Be warm, supportive, and non-judgmental.
- Always acknowledge the user's feelings before offering analysis.
- Use the structured analysis results provided below to ground your answer in evidence.
- When Bazi results are available: mention five elements (五行) and zodiac compatibility naturally.
- When psychology results are available: reference attachment styles and communication patterns.
- When tarot results are available: interpret the symbolic meaning in context.
- Never make absolute predictions. Use "may", "tends to", "it's possible that".
- Always end with a thoughtful question to continue the conversation.
- Keep responses under 500 words unless the user asks for detailed analysis.
"""


class PromptBuilderService:
    def build_system_prompt(
        self,
        memory_context: dict | None = None,
        structured_result: StructuredResult | None = None,
    ) -> str:
        parts = [SYSTEM_BASE]

        # Week 6: tool analysis results
        if structured_result and structured_result.tool_results:
            parts.append("\n--- Structured Analysis Results ---")
            for tr in structured_result.tool_results:
                parts.append(f"\n[{tr.tool.upper()}] Status: {tr.status}")
                if tr.core_signals:
                    parts.append(f"  Core signals: {', '.join(tr.core_signals)}")
                if tr.risks:
                    parts.append(f"  Risks: {', '.join(tr.risks)}")
                if tr.opportunities:
                    parts.append(f"  Opportunities: {', '.join(tr.opportunities)}")
                if tr.actions:
                    parts.append(f"  Actions: {', '.join(tr.actions)}")
            if structured_result.summary:
                parts.append(f"\nSummary: {structured_result.summary}")
            parts.append("--- End Analysis ---")

        # Week 5: memory context
        if memory_context:
            if memory_context.get("profile"):
                p = memory_context["profile"]
                parts.append("\nCurrent relationship context:")
                for attr in ["current_status", "current_goal", "relationship_stage",
                             "trust_level", "conflict_level", "intimacy_level"]:
                    val = getattr(p, attr, None)
                    if val:
                        parts.append(f"- {attr}: {val}")

            if memory_context.get("summary"):
                parts.append(f"\nRelationship memory: {memory_context['summary'].summary}")

            if memory_context.get("recent_events"):
                events = memory_context["recent_events"]
                if events:
                    parts.append("\nKey events:")
                    for e in events[:5]:
                        parts.append(f"- [{e.event_type}] {e.description[:100]}")

        return "\n".join(parts)

    def build_consultation_prompt(
        self,
        *,
        user_message: str,
        analysis_methods: list[str] | None,
        partner_id: str | None,
        memory_context: dict | None = None,
    ) -> str:
        methods = analysis_methods or DEFAULT_ANALYSIS_METHODS
        parts = [
            f"analysis_methods: {', '.join(methods)}",
            f"partner_id: {partner_id or 'unknown'}",
            f"user_message: {user_message}",
        ]
        return "\n".join(parts)
