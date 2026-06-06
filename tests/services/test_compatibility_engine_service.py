from types import SimpleNamespace

from app.services.compatibility_engine_service import CompatibilityEngineService
from app.tools.result_schema import ToolResult


def test_serialize_relationship_context_handles_orm_like_objects():
    profile = SimpleNamespace(
        current_status="breakup",
        current_goal="reconciliation",
        relationship_stage="no_contact",
        trust_level="low",
        conflict_level="high",
        intimacy_level="medium",
        summary_snapshot="snapshot",
    )
    summary = SimpleNamespace(summary="long term memory", summary_version=1)
    event = SimpleNamespace(
        event_type="breakup",
        event_date=None,
        description="They broke up last week",
        confidence_score=0.95,
    )

    data = CompatibilityEngineService._serialize_relationship_context(
        {
            "profile": profile,
            "summary": summary,
            "recent_events": [event],
        }
    )

    assert data["profile"]["current_status"] == "breakup"
    assert data["summary"]["summary"] == "long term memory"
    assert data["recent_events"][0]["event_type"] == "breakup"


def test_synthesize_does_not_degrade_on_serializable_memory_context():
    engine = CompatibilityEngineService()
    bazi = ToolResult(
        tool="bazi",
        status="ok",
        core_signals=["signal"],
        risks=[],
        opportunities=[],
        actions=["action"],
        confidence_notes="",
    )
    profile = SimpleNamespace(current_status="breakup")
    summary = SimpleNamespace(summary="memory", summary_version=1)

    result = engine.synthesize(
        bazi_result=bazi,
        psychology_result=None,
        tarot_result=None,
        relationship_context={
            "profile": profile,
            "summary": summary,
            "recent_events": [],
        },
    )

    assert result.tool == "compatibility"
    assert result.status in {"ok", "degraded"}


def test_synthesize_degrades_on_invalid_json(monkeypatch):
    engine = CompatibilityEngineService()

    monkeypatch.setattr(engine.prompt_center, "get_or_default", lambda name, default: default)
    monkeypatch.setattr(engine.llm, "generate_text", lambda system, user: "not-json")

    result = engine.synthesize(
        bazi_result=None,
        psychology_result=None,
        tarot_result=None,
        relationship_context=None,
    )

    assert result.tool == "compatibility"
    assert result.status == "degraded"
