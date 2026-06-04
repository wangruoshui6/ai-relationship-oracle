"""LLM-driven Tarot Engine — symbolic card interpretation for relationships."""
import json
import random
from app.tools.base import BaseTool
from app.tools.result_schema import ToolResult
from app.services.llm_provider_service import LLMProviderService


MAJOR_ARCANA = [
    ("0", "The Fool", "new beginnings, spontaneity, leap of faith"),
    ("I", "The Magician", "willpower, manifestation, resourcefulness"),
    ("II", "The High Priestess", "intuition, subconscious, divine feminine"),
    ("III", "The Empress", "nurturing, abundance, sensuality"),
    ("IV", "The Emperor", "authority, structure, control"),
    ("V", "The Hierophant", "tradition, spiritual guidance, conformity"),
    ("VI", "The Lovers", "love, harmony, choices, alignment of values"),
    ("VII", "The Chariot", "determination, willpower, overcoming obstacles"),
    ("VIII", "Strength", "courage, compassion, inner power"),
    ("IX", "The Hermit", "introspection, solitude, inner guidance"),
    ("X", "Wheel of Fortune", "cycles, destiny, turning point"),
    ("XI", "Justice", "fairness, truth, cause and effect"),
    ("XII", "The Hanged Man", "surrender, new perspective, letting go"),
    ("XIII", "Death", "endings, transformation, rebirth"),
    ("XIV", "Temperance", "balance, moderation, patience"),
    ("XV", "The Devil", "temptation, materialism, shadow self"),
    ("XVI", "The Tower", "sudden upheaval, breakthrough, revelation"),
    ("XVII", "The Star", "hope, inspiration, serenity"),
    ("XVIII", "The Moon", "illusion, fear, the subconscious"),
    ("XIX", "The Sun", "joy, success, vitality"),
    ("XX", "Judgement", "reckoning, awakening, inner calling"),
    ("XXI", "The World", "completion, integration, accomplishment"),
]

TAROT_SYSTEM_PROMPT = """You are a tarot reader specializing in relationship questions. You draw one card and interpret its meaning in the context of the querent's situation.

Output MUST be valid JSON with these exact keys:
{
  "card_name": "The card name (e.g. The Star)",
  "card_meaning": "1-2 sentence traditional meaning of this card in relationships",
  "core_signals": ["3-5 symbolic insights from this card relevant to the situation"],
  "risks": ["2-3 shadow aspects or warnings of this card"],
  "opportunities": ["2-3 positive potentials this card reveals"],
  "actions": ["2-3 practical steps inspired by this card's wisdom"]
}

Rules:
- Interpret the card in direct relation to the user's question.
- Include the upright or reversed aspect (I will tell you which it is).
- Be poetic but grounded. Use the card's traditional symbolism.
- All array values must be strings.
"""


class TarotEngineService(BaseTool):
    tool_name = "tarot"

    def __init__(self) -> None:
        self.llm = LLMProviderService()

    def analyze(self, data: dict) -> ToolResult:
        user_message = data.get("user_message", "")
        card = self._draw_card()
        reversed_ = random.random() < 0.3  # 30% chance reversed
        orientation = "reversed" if reversed_ else "upright"

        prompt = f"""The querent asks: "{user_message}"

Card drawn: {card[1]} (Arcana {card[0]}) — {orientation}
Traditional keywords: {card[2]}

Interpret this card in the context of the querent's relationship question. The card is {orientation}."""

        try:
            raw = self.llm.generate_text(TAROT_SYSTEM_PROMPT, prompt)
            parsed = self._parse_json(raw)
            return ToolResult(
                tool=self.tool_name,
                status="ok",
                core_signals=[f"card: {parsed.get('card_name', card[1])} ({orientation})"] + parsed.get("core_signals", []),
                risks=parsed.get("risks", []),
                opportunities=parsed.get("opportunities", []),
                actions=parsed.get("actions", []),
                confidence_notes=f"Tarot provides symbolic guidance, not predictions. Card meaning: {parsed.get('card_meaning', '')}",
            )
        except Exception:
            return ToolResult(
                tool=self.tool_name,
                status="degraded",
                core_signals=[f"card: {card[1]} ({orientation})"],
                risks=[],
                opportunities=[],
                actions=["Reflect on what this card means to you personally"],
                confidence_notes=f"Tarot interpretation unavailable. Traditional meaning: {card[2]}.",
            )

    def _draw_card(self) -> tuple[str, str, str]:
        return random.choice(MAJOR_ARCANA)

    @staticmethod
    def _parse_json(raw: str) -> dict:
        raw = raw.strip()
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[-1]
            if raw.endswith("```"):
                raw = raw[:-3]
            raw = raw.strip()
        return json.loads(raw)
