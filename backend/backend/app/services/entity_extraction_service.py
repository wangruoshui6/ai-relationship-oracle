import re

STOPWORDS = {"the","she","her","you","and","but","for","has","was","did",
             "can","not","one","our","out","how","are","its","his","him","had"}

class EntityExtractionService:
    def extract(self, user_message: str) -> dict[str, str | None]:
        return {
            "partner_name": self._extract_partner_name(user_message),
            "current_status": self._infer_status(user_message),
            "current_goal": self._infer_goal(user_message),
        }

    def _extract_partner_name(self, user_message: str) -> str | None:
        # English names (filter stopwords)
        match = re.search(r"\b([A-Z][a-zA-Z]{1,30})\b", user_message)
        if match:
            name = match.group(1)
            if name.lower() not in STOPWORDS:
                return name

        # Chinese name patterns
        patterns = [r"和(.{1,8})分手", r"跟(.{1,8})分手",
                    r"和(.{1,8})最近", r"跟(.{1,8})最近"]
        for pat in patterns:
            m = re.search(pat, user_message)
            if m:
                c = m.group(1).strip()
                if c and c not in {"他","她","对方"}:
                    return c
        return None

    def _infer_status(self, user_message: str) -> str | None:
        msg = user_message.lower()
        if "分手" in user_message or any(k in msg for k in ["broke up","breakup","split up","broken up"]):
            return "breakup"
        if "暧昧" in user_message or "ambiguous" in msg:
            return "ambiguous"
        if "吵架" in user_message or any(k in msg for k in ["fight","argue","fought","conflict"]):
            return "conflict"
        return None

    def _infer_goal(self, user_message: str) -> str | None:
        msg = user_message.lower()
        if any(k in user_message for k in ["复合","回来","挽回"]) or any(k in msg for k in ["come back","get back","reconcile"]):
            return "reconciliation"
        if any(k in user_message for k in ["结婚","长期"]) or any(k in msg for k in ["marry","long term"]):
            return "long_term_commitment"
        return None
