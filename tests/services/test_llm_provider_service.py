import pytest

from app.core.exceptions import AppException
from app.services.llm_provider_service import LLMProviderService


def test_generate_text_without_api_key_returns_stub():
    service = LLMProviderService()
    service.api_key = ""

    result = service.generate_text("system", "hello")

    assert "[Stub]" in result


def test_generate_text_raises_app_exception_on_provider_failure():
    service = LLMProviderService()
    service.api_key = "fake-key"
    service.base_url = "http://127.0.0.1:9"

    with pytest.raises(AppException) as exc:
        service.generate_text("system", "hello")

    assert exc.value.code == 2002
