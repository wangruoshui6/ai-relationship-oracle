from app.core.constants import DEFAULT_ANALYSIS_METHODS


class PromptBuilderService:
    def build_consultation_prompt(
        self,
        *,
        user_message: str,
        analysis_methods: list[str] | None,
        partner_id: str | None,
    ) -> str:
        methods = analysis_methods or DEFAULT_ANALYSIS_METHODS
        partner_text = partner_id or "unknown"
        return (
            "You are AI Relationship Oracle.\n"
            f"analysis_methods: {', '.join(methods)}\n"
            f"partner_id: {partner_text}\n"
            f"user_message: {user_message}"
        )
