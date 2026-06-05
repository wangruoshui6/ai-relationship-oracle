from app.services.tarot_engine_service import TarotEngineService


def test_tarot_engine_degrades_on_invalid_json(monkeypatch):
    service = TarotEngineService()

    monkeypatch.setattr(service.prompt_center, "get_or_default", lambda name, default: default)
    monkeypatch.setattr(service.llm, "generate_text", lambda system, user: "not-json")

    result = service.analyze({"user_message": "Will she come back?"})

    assert result.status == "degraded"
    assert result.tool == "tarot"
