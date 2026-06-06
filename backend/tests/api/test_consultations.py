def build_auth_headers(client, email: str = "consult@example.com"):
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


def test_consultation_creates_conversation_if_missing(client):
    headers = build_auth_headers(client)
    response = client.post(
        "/api/v1/consultations",
        headers=headers,
        json={
            "conversation_id": None,
            "partner_id": None,
            "message": "I keep fighting with her, what should I do?",
            "analysis_methods": ["bazi", "psychology"],
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["code"] == 0
    assert payload["data"]["conversation_id"]
    assert payload["data"]["answer"]
    assert len(payload["data"]["answer"]) > 10
    assert payload["data"]["report_generated"] is False


def test_consultation_without_partner_id(client):
    headers = build_auth_headers(client, email="consult2@example.com")
    response = client.post(
        "/api/v1/consultations",
        headers=headers,
        json={"message": "I want to talk about this relationship"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["data"]["partner_id"] is None
    # With real LLM, answer is natural text, not an echo of the message
    assert payload["data"]["answer"]
    assert len(payload["data"]["answer"]) > 10


def test_consultation_persists_user_and_assistant_message(client):
    headers = build_auth_headers(client, email="consult3@example.com")
    consult_response = client.post(
        "/api/v1/consultations",
        headers=headers,
        json={"message": "She has been cold recently"},
    )
    conversation_id = consult_response.json()["data"]["conversation_id"]

    detail_response = client.get(
        f"/api/v1/conversations/{conversation_id}", headers=headers
    )
    payload = detail_response.json()

    assert detail_response.status_code == 200
    assert len(payload["data"]["messages"]) == 2
    assert payload["data"]["messages"][0]["role"] == "user"
    assert payload["data"]["messages"][1]["role"] == "assistant"


def test_consultation_stream_returns_sse_events(client):
    headers = build_auth_headers(client, email="consult-stream@example.com")
    response = client.post(
        "/api/v1/consultations/stream",
        headers=headers,
        json={"message": "I miss her and want to know if we can reconcile."},
    )

    assert response.status_code == 200
    assert "text/event-stream" in response.headers["content-type"]
    assert "event: status" in response.text
    assert "event: done" in response.text


def test_consultation_rejects_partner_mismatch_for_existing_conversation(client):
    headers = build_auth_headers(client, email="consult4@example.com")
    partner_a = client.post(
        "/api/v1/partners",
        headers=headers,
        json={"nickname": "Sarah"},
    ).json()["data"]["id"]
    partner_b = client.post(
        "/api/v1/partners",
        headers=headers,
        json={"nickname": "Amy"},
    ).json()["data"]["id"]

    first = client.post(
        "/api/v1/consultations",
        headers=headers,
        json={
            "partner_id": partner_a,
            "message": "First consultation with Sarah",
        },
    )
    conversation_id = first.json()["data"]["conversation_id"]

    second = client.post(
        "/api/v1/consultations",
        headers=headers,
        json={
            "conversation_id": conversation_id,
            "partner_id": partner_b,
            "message": "Now ask about Amy in the same conversation",
        },
    )

    assert second.status_code == 409
    payload = second.json()
    assert payload["code"] == 1005
