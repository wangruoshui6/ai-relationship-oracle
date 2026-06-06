from app.core.exceptions import AppException
from app.services.llm_provider_service import LLMProviderService


def build_auth_headers(client, email: str = "resilience@example.com"):
    client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "password123"},
    )
    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "password123"},
    )
    token = login_response.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_consultation_persists_user_message_and_fallback_assistant_on_llm_failure(client, monkeypatch):
    headers = build_auth_headers(client)

    def fail_llm(self, system_prompt: str, user_message: str) -> str:
        raise AppException(code=2002, message="llm provider error", status_code=502)

    monkeypatch.setattr(LLMProviderService, "generate_text", fail_llm)

    response = client.post(
        "/api/v1/consultations",
        headers=headers,
        json={"message": "I broke up with Sarah last week."},
    )

    assert response.status_code == 200
    payload = response.json()["data"]
    assert "temporary issue" in payload["answer"]

    detail = client.get(f"/api/v1/conversations/{payload['conversation_id']}", headers=headers)
    messages = detail.json()["data"]["messages"]
    assert len(messages) == 2
    assert messages[0]["role"] == "user"
    assert messages[1]["role"] == "assistant"
    assert "temporary issue" in messages[1]["content"]
