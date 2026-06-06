from app.services.psychology_engine_service import PsychologyEngineService


def test_psychology_engine_degrades_on_invalid_json(monkeypatch):
    service = PsychologyEngineService()

    monkeypatch.setattr(service.prompt_center, "get_or_default", lambda name, default: default)
    monkeypatch.setattr(service.llm, "generate_text", lambda system, user: "not-json")

    result = service.analyze({"user_message": "He is hot and cold"})

    assert result.status == "degraded"
    assert result.tool == "psychology"
