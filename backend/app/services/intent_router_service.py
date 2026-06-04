class IntentRouterService:
    def detect_intent(self, user_message: str) -> str:
        message = user_message.lower()
        if any(keyword in message for keyword in ["你好", "hello", "hi"]):
            return "greeting"
        if any(keyword in message for keyword in ["事业", "财富", "法律", "健康"]):
            return "general_guidance"
        return "relationship_analysis"
