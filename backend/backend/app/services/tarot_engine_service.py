"""LLM-driven Tarot Engine ? uses PromptCenter for prompt management."""
import json, random
from app.tools.base import BaseTool
from app.tools.result_schema import ToolResult
from app.services.llm_provider_service import LLMProviderService
from app.services.prompt_center_service import get_prompt_center

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


class TarotEngineService(BaseTool):
    tool_name = "tarot"
    DEFAULT_TAROT_PROMPT = (
        "You interpret a tarot card for a relationship question. Return JSON with keys: "
        "card_name, card_meaning, core_signals, risks, opportunities, actions."
    )

    def __init__(self) -> None:
        self.prompt_center = get_prompt_center()
        self.llm = LLMProviderService()

    def analyze(self, data: dict) -> ToolResult:
        user_message = data.get("user_message", "")
        card = self._draw_card()
        reversed_ = random.random() < 0.3
        orientation = "reversed" if reversed_ else "upright"

        prompt = (
            f'The querent asks: "{user_message}"\n\n'
            f"Card drawn: {card[1]} (Arcana {card[0]}) - {orientation}\n"
            f"Traditional keywords: {card[2]}\n\n"
            f"Interpret this card in the context of the querent's relationship question. The card is {orientation}."
        )

        try:
            system_prompt = self.prompt_center.get_or_default(
                "tarot",
                self.DEFAULT_TAROT_PROMPT,
            )
            raw = self.llm.generate_text(system_prompt, prompt)
            parsed = self._parse_json(raw)
            if not parsed:
                raise ValueError("empty tarot json")
            return ToolResult(
                tool=self.tool_name, status="ok",
                core_signals=[f"card: {parsed.get('card_name', card[1])} ({orientation})"] + parsed.get("core_signals", []),
                risks=parsed.get("risks", []),
                opportunities=parsed.get("opportunities", []),
                actions=parsed.get("actions", []),
                confidence_notes=f"Tarot provides symbolic guidance, not predictions. Card meaning: {parsed.get('card_meaning', '')}",
            )
        except Exception:
            return ToolResult(
                tool=self.tool_name, status="degraded",
                core_signals=[f"card: {card[1]} ({orientation})"],
                risks=[], opportunities=[],
                actions=["Reflect on what this card means to you personally"],
                confidence_notes=f"Tarot interpretation unavailable. Traditional meaning: {card[2]}.",
            )

    def _draw_card(self) -> tuple[str, str, str]:
        return random.choice(MAJOR_ARCANA)

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
