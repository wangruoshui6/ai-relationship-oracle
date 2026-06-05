"""LLM Provider Service — real OpenAI-compatible API (DeepSeek)."""
import httpx

from app.core.config import get_settings
from app.core.exceptions import AppException


class LLMProviderService:
    def __init__(self) -> None:
        settings = get_settings()
        self.base_url = settings.llm_base_url.rstrip("/")
        self.api_key = settings.llm_api_key
        self.model = settings.llm_model
        self._client = httpx.Client(timeout=httpx.Timeout(30.0))

    def generate_text(self, system_prompt: str, user_message: str) -> str:
        if not self.api_key:
            return self._fallback(user_message)

        try:
            response = self._client.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_message},
                    ],
                    "temperature": 0.7,
                    "max_tokens": 1024,
                },
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
        except Exception as e:
            raise AppException(
                code=2002,
                message=f"llm provider error: {e}",
                status_code=502,
            ) from e

    def generate_text_with_messages(self, messages: list[dict]) -> str:
        if not self.api_key:
            return self._fallback(str(messages[-1].get("content", "")) if messages else "")

        try:
            response = self._client.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": 1024,
                },
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            raise AppException(
                code=2002,
                message=f"llm provider error: {e}",
                status_code=502,
            ) from e

    @staticmethod
    def _fallback(user_message: str) -> str:
        preview = user_message[:60]
        return f"[Stub] No API key configured. Received: {preview}..."
