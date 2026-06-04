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
            "message": "我和她最近总是吵架，我该怎么办？",
            "analysis_methods": ["bazi", "psychology"],
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["code"] == 0
    assert payload["data"]["conversation_id"]
    assert payload["data"]["answer"]
    assert payload["data"]["report_generated"] is False


def test_consultation_without_partner_id(client):
    headers = build_auth_headers(client, email="consult2@example.com")
    response = client.post(
        "/api/v1/consultations",
        headers=headers,
        json={
            "message": "我想聊聊这段关系",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["data"]["partner_id"] is None
    assert "我想聊聊这段关系" in payload["data"]["answer"]


def test_consultation_persists_user_and_assistant_message(client):
    headers = build_auth_headers(client, email="consult3@example.com")
    consult_response = client.post(
        "/api/v1/consultations",
        headers=headers,
        json={
            "message": "她最近有点冷淡",
        },
    )
    conversation_id = consult_response.json()["data"]["conversation_id"]

    detail_response = client.get(f"/api/v1/conversations/{conversation_id}", headers=headers)
    payload = detail_response.json()

    assert detail_response.status_code == 200
    assert len(payload["data"]["messages"]) == 2
    assert payload["data"]["messages"][0]["role"] == "user"
    assert payload["data"]["messages"][1]["role"] == "assistant"
