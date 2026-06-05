from app.services.prompt_center_service import PromptCenterService


def test_get_or_default_returns_default_for_missing_prompt():
    service = PromptCenterService()

    result = service.get_or_default("missing-prompt", "fallback prompt")

    assert result == "fallback prompt"
