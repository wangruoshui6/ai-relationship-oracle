"""Week 6: Bazi Engine — five elements, zodiac compatibility with real chart data."""
from app.tools.base import BaseTool
from app.tools.result_schema import ToolResult


ZODIAC = ["rat", "ox", "tiger", "rabbit", "dragon", "snake",
          "horse", "goat", "monkey", "rooster", "dog", "pig"]
CHINESE_TO_EN_ZODIAC = {
    "鼠": "rat", "牛": "ox", "虎": "tiger", "兔": "rabbit",
    "龙": "dragon", "蛇": "snake", "马": "horse", "羊": "goat",
    "猴": "monkey", "鸡": "rooster", "狗": "dog", "猪": "pig",
}
ZODIAC_TRIADS = [
    {"rat", "dragon", "monkey"}, {"ox", "snake", "rooster"},
    {"tiger", "horse", "dog"}, {"rabbit", "goat", "pig"},
]
ZODIAC_CLASHES = [
    {"rat", "horse"}, {"ox", "goat"}, {"tiger", "monkey"},
    {"rabbit", "rooster"}, {"dragon", "dog"}, {"snake", "pig"},
]


class BaziEngineService(BaseTool):
    tool_name = "bazi"

    def analyze(self, data: dict) -> ToolResult:
        chart = data.get("bazi_chart")

        if not chart or chart == {} or chart.get("day_master") is None:
            return ToolResult(
                tool=self.tool_name,
                status="degraded",
                core_signals=["insufficient birth data"],
                risks=[],
                opportunities=[],
                actions=["Provide your birth date and time for a personalized Bazi reading"],
                confidence_notes="Cannot compute Bazi chart without birth date.",
            )

        signals = []
        risks = []
        opportunities = []
        actions = []

        # Day Master analysis
        day_master = chart.get("day_master", "unknown")
        day_element = chart.get("day_master_element", "unknown")
        signals.append(f"day master: {day_master}({day_element})")
        signals.append(f"zodiac: {self._zodiac_name(chart.get('zodiac', 'unknown'))}")

        # Five elements distribution
        elements = (data.get("five_elements") or {}).get("counts", {})
        if elements:
            dominant = max(elements, key=elements.get)
            signals.append(f"dominant element: {dominant} ({elements[dominant]} of 8)")

            if elements.get("火", 0) >= 2:
                signals.append("strong fire: passionate, expressive, but prone to impulsivity")
            if elements.get("水", 0) >= 2:
                signals.append("strong water: emotionally deep, intuitive, adaptable")
            if elements.get("木", 0) >= 2:
                signals.append("strong wood: growth-driven, idealistic, resilient")
            if elements.get("金", 0) >= 2:
                signals.append("strong metal: principled, disciplined, organized")
            if elements.get("土", 0) >= 2:
                signals.append("strong earth: stable, nurturing, grounded")

            # Element imbalance
            weak = [k for k, v in elements.items() if v == 0]
            if weak:
                signals.append(f"weak elements: {','.join(weak)}")

            # Day master element advice
            if day_element == "火" and elements.get("火", 0) <= 1:
                risks.append("weak fire: may lack confidence and self-expression in conflict")
                actions.append("Wear red or warm colors on important days to boost fire energy")
            elif day_element == "水" and elements.get("水", 0) <= 1:
                risks.append("weak water: may struggle with emotional boundaries")
                actions.append("Spend time near water (lake, river) to recharge your water element")

            if elements.get("金", 0) >= 3:
                risks.append("excess metal: may be overly rigid in expectations of partner")

        # Zodiac compatibility
        user_zodiac_cn = chart.get("zodiac")
        partner_zodiac_cn = data.get("partner_zodiac")
        if user_zodiac_cn and partner_zodiac_cn:
            user_en = CHINESE_TO_EN_ZODIAC.get(user_zodiac_cn, user_zodiac_cn)
            partner_en = CHINESE_TO_EN_ZODIAC.get(partner_zodiac_cn, partner_zodiac_cn)
            zodiac_notes = self._zodiac_compatibility(user_en, partner_en)
            signals.extend(zodiac_notes)

        # Pillars detail
        pillars = chart.get("pillars", [])
        pillar_text = " | ".join(
            f"{p['pillar']}:{p['stem']}{p['branch']}" for p in pillars
        )
        actions.append(f"Your Bazi: {pillar_text}")

        # Default advice
        if not chart.get("has_birth_time"):
            confidence = "Missing birth time; hour pillar not computed. Accuracy reduced by ~20%."
        else:
            confidence = None

        opportunities.append("Use your dominant element strengths in relationship communication")
        actions.append("Track emotional patterns aligned with your day master element")

        return ToolResult(
            tool=self.tool_name,
            status="ok",
            core_signals=signals,
            risks=risks,
            opportunities=opportunities,
            actions=actions,
            confidence_notes=confidence,
        )

    def _zodiac_compatibility(self, user: str, partner: str) -> list[str]:
        if user == "unknown" or partner == "unknown":
            return []
        notes = []
        pair = {user, partner}
        for triad in ZODIAC_TRIADS:
            if pair.issubset(triad):
                notes.append(f"zodiac harmony: {user}<->{partner} in same triad (natural affinity)")
                return notes
        for clash in ZODIAC_CLASHES:
            if pair == clash:
                notes.append(f"zodiac clash: {user}<->{partner} opposing energies (conscious effort needed)")
                return notes
        notes.append(f"zodiac neutral: {user}<->{partner}")
        return notes

    @staticmethod
    def _zodiac_name(cn: str) -> str:
        en = CHINESE_TO_EN_ZODIAC.get(cn, cn)
        return f"{cn}({en})"
