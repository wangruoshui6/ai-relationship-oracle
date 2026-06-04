class LLMProviderService:
    def generate_text(self, prompt: str) -> str:
        # Week 3 uses a deterministic stub so we can keep the consultation
        # flow testable before wiring a real model provider.
        preview = prompt.strip().splitlines()[-1] if prompt.strip() else ""
        return f"这是一个最小可用咨询回复。已收到你的问题：{preview}"
