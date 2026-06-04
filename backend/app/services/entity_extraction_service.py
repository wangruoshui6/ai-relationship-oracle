import re


class EntityExtractionService:
    def extract(self, user_message: str) -> dict[str, str | None]:
        partner_name = self._extract_partner_name(user_message)
        current_status = self._infer_status(user_message)
        current_goal = self._infer_goal(user_message)
        return {
            "partner_name": partner_name,
            "current_status": current_status,
            "current_goal": current_goal,
        }

    def _extract_partner_name(self, user_message: str) -> str | None:
        english_name_match = re.search(r"\b([A-Z][a-zA-Z]{1,30})\b", user_message)
        if english_name_match:
            return english_name_match.group(1)

        chinese_patterns = [
            r"和(.{1,8})分手",
            r"跟(.{1,8})分手",
            r"和(.{1,8})最近",
            r"跟(.{1,8})最近",
        ]
        for pattern in chinese_patterns:
            match = re.search(pattern, user_message)
            if match:
                candidate = match.group(1).strip()
                if candidate and candidate not in {"他", "她", "对方"}:
                    return candidate
        return None

    def _infer_status(self, user_message: str) -> str | None:
        if "分手" in user_message:
            return "breakup"
        if "暧昧" in user_message:
            return "ambiguous"
        if "吵架" in user_message:
            return "conflict"
        return None

    def _infer_goal(self, user_message: str) -> str | None:
        if any(keyword in user_message for keyword in ["复合", "回来", "挽回"]):
            return "reconciliation"
        if any(keyword in user_message for keyword in ["结婚", "长期"]):
            return "long_term_commitment"
        return None
