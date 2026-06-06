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
ELEMENT_GENERATES = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}
ELEMENT_CONTROLS = {"木": "土", "土": "水", "水": "火", "火": "金", "金": "木"}
BRANCH_CLASHES = {
    ("子", "午"), ("丑", "未"), ("寅", "申"),
    ("卯", "酉"), ("辰", "戌"), ("巳", "亥"),
}


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

        partner_chart = data.get("partner_bazi_chart")
        partner_elements = self._count_elements_from_chart(partner_chart) if partner_chart else {}
        partner_day_master = None
        partner_day_element = None

        if partner_chart:
            partner_day_master = partner_chart.get("day_master", "unknown")
            partner_day_element = partner_chart.get("day_master_element", "unknown")
            signals.append(f"partner day master: {partner_day_master}({partner_day_element})")
            signals.append(f"partner zodiac: {self._zodiac_name(partner_chart.get('zodiac', 'unknown'))}")

            if partner_elements:
                dominant_partner = max(partner_elements, key=partner_elements.get)
                signals.append(
                    f"partner dominant element: {dominant_partner} ({partner_elements[dominant_partner]} of 8)"
                )

            relation_signal, relation_risks, relation_opportunities, relation_actions = (
                self._day_master_relation(day_element, partner_day_element)
            )
            if relation_signal:
                signals.append(relation_signal)
            risks.extend(relation_risks)
            opportunities.extend(relation_opportunities)
            actions.extend(relation_actions)

            complement_signal, complement_risks, complement_opps = self._element_balance_relation(
                elements,
                partner_elements,
            )
            if complement_signal:
                signals.append(complement_signal)
            risks.extend(complement_risks)
            opportunities.extend(complement_opps)

            pillar_notes, pillar_risks, pillar_actions = self._pillar_interactions(
                chart.get("pillars", []),
                partner_chart.get("pillars", []),
            )
            signals.extend(pillar_notes)
            risks.extend(pillar_risks)
            actions.extend(pillar_actions)

        # Zodiac compatibility remains auxiliary, not the main pair judgment
        user_zodiac_cn = chart.get("zodiac")
        partner_zodiac_cn = (
            partner_chart.get("zodiac") if partner_chart else data.get("partner_zodiac")
        )
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
        if partner_chart:
            partner_pillars = partner_chart.get("pillars", [])
            partner_pillar_text = " | ".join(
                f"{p['pillar']}:{p['stem']}{p['branch']}" for p in partner_pillars
            )
            actions.append(f"Partner Bazi: {partner_pillar_text}")

        # Default advice
        if not chart.get("has_birth_time"):
            confidence = "Missing birth time; hour pillar not computed. Accuracy reduced by ~20%."
        elif partner_chart and not partner_chart.get("has_birth_time"):
            confidence = "Partner birth time is missing; pair analysis is partially reduced."
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

    @staticmethod
    def _count_elements_from_chart(chart: dict | None) -> dict[str, int]:
        if not chart:
            return {}
        counts = {"木": 0, "火": 0, "土": 0, "金": 0, "水": 0}
        for pillar in chart.get("pillars", []):
            stem_element = pillar.get("stem_element")
            branch_element = pillar.get("branch_element")
            if stem_element in counts:
                counts[stem_element] += 1
            if branch_element in counts:
                counts[branch_element] += 1
        return counts

    def _day_master_relation(
        self, user_element: str, partner_element: str | None
    ) -> tuple[str | None, list[str], list[str], list[str]]:
        if not partner_element:
            return None, [], [], []

        risks: list[str] = []
        opportunities: list[str] = []
        actions: list[str] = []

        if user_element == partner_element:
            return (
                f"day master relation: both of you share the {user_element} element, which increases instinctive resonance",
                [],
                ["shared elemental nature can make emotional understanding faster"],
                ["Avoid mirroring each other's weaknesses when conflict rises"],
            )

        if ELEMENT_GENERATES.get(user_element) == partner_element:
            return (
                f"day master relation: your {user_element} nourishes partner's {partner_element}",
                [],
                ["your natural style can support the other person's emotional growth"],
                ["Keep the relationship balanced so support does not become over-giving"],
            )

        if ELEMENT_GENERATES.get(partner_element) == user_element:
            return (
                f"day master relation: partner's {partner_element} nourishes your {user_element}",
                [],
                ["the partner may naturally steady or replenish you"],
                ["Do not become overly dependent on the partner for emotional regulation"],
            )

        if ELEMENT_CONTROLS.get(user_element) == partner_element:
            risks.append(
                f"your {user_element} controls partner's {partner_element}, which can create pressure or imbalance"
            )
            actions.append("Be careful not to push too hard when trying to lead the relationship")
            return (
                f"day master relation: your {user_element} restrains partner's {partner_element}",
                risks,
                [],
                actions,
            )

        if ELEMENT_CONTROLS.get(partner_element) == user_element:
            risks.append(
                f"partner's {partner_element} controls your {user_element}, which can make you feel constrained"
            )
            actions.append("Name hidden resentment early instead of silently accumulating it")
            return (
                f"day master relation: partner's {partner_element} restrains your {user_element}",
                risks,
                [],
                actions,
            )

        return (
            f"day master relation: your {user_element} and partner's {partner_element} have a mixed but workable dynamic",
            [],
            ["this pairing can complement each other if rhythm and expectations are aligned"],
            ["Translate differences into concrete communication rules"],
        )

    def _element_balance_relation(
        self,
        user_counts: dict[str, int],
        partner_counts: dict[str, int],
    ) -> tuple[str | None, list[str], list[str]]:
        if not user_counts or not partner_counts:
            return None, [], []

        user_missing = {element for element, value in user_counts.items() if value == 0}
        partner_missing = {element for element, value in partner_counts.items() if value == 0}

        complementary = sorted(user_missing.intersection(
            {element for element, value in partner_counts.items() if value >= 2}
        ))
        mutual_gaps = sorted(user_missing.intersection(partner_missing))

        risks: list[str] = []
        opportunities: list[str] = []
        signal_parts: list[str] = []

        if complementary:
            signal_parts.append(
                f"partner supplements your missing elements: {', '.join(complementary)}"
            )
            opportunities.append(
                "your elemental gaps may be softened by the partner's natural strengths"
            )

        reverse_complementary = sorted(partner_missing.intersection(
            {element for element, value in user_counts.items() if value >= 2}
        ))
        if reverse_complementary:
            signal_parts.append(
                f"you supplement partner's missing elements: {', '.join(reverse_complementary)}"
            )
            opportunities.append(
                "you may naturally provide strengths the partner finds difficult to stabilize alone"
            )

        if mutual_gaps:
            risks.append(
                f"both charts are weak in {', '.join(mutual_gaps)}, so that area may become a shared blind spot"
            )
            signal_parts.append(
                f"shared weak elements: {', '.join(mutual_gaps)}"
            )

        if not signal_parts:
            signal_parts.append("five-element balance: no strong complement or conflict detected")

        return "; ".join(signal_parts), risks, opportunities

    def _pillar_interactions(
        self,
        user_pillars: list[dict],
        partner_pillars: list[dict],
    ) -> tuple[list[str], list[str], list[str]]:
        if not user_pillars or not partner_pillars:
            return [], [], []

        notes: list[str] = []
        risks: list[str] = []
        actions: list[str] = []

        user_branches = [pillar.get("branch") for pillar in user_pillars if pillar.get("branch")]
        partner_branches = [pillar.get("branch") for pillar in partner_pillars if pillar.get("branch")]
        shared_branches = sorted(set(user_branches).intersection(partner_branches))

        if shared_branches:
            notes.append(
                f"shared branch resonance: {', '.join(shared_branches)} appear in both charts"
            )

        clashes = []
        for ub in user_branches:
            for pb in partner_branches:
                if (ub, pb) in BRANCH_CLASHES or (pb, ub) in BRANCH_CLASHES:
                    clashes.append(f"{ub}-{pb}")

        if clashes:
            risks.append(
                f"branch clashes present: {', '.join(sorted(set(clashes)))}; timing and temperament may easily misalign"
            )
            actions.append("When emotions escalate, slow the pace instead of forcing resolution immediately")

        if shared_branches and not clashes:
            actions.append("Use naturally shared rhythms to build predictable routines together")

        return notes, risks, actions
