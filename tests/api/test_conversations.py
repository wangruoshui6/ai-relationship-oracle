def build_auth_headers(client, email: str = "conversation@example.com"):
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


def create_conversation_via_consultation(client, headers):
    response = client.post(
        "/api/v1/consultations",
        headers=headers,
        json={"message": "这是一个测试咨询"},
    )
    return response.json()["data"]["conversation_id"]


def test_get_conversation_detail(client):
    headers = build_auth_headers(client)
    conversation_id = create_conversation_via_consultation(client, headers)

    response = client.get(f"/api/v1/conversations/{conversation_id}", headers=headers)

    assert response.status_code == 200
    payload = response.json()
    assert payload["code"] == 0
    assert payload["data"]["id"] == conversation_id
    assert len(payload["data"]["messages"]) == 2


def test_list_conversations(client):
    headers = build_auth_headers(client, email="conversation2@example.com")
    create_conversation_via_consultation(client, headers)
    create_conversation_via_consultation(client, headers)

    response = client.get("/api/v1/conversations", headers=headers)

    assert response.status_code == 200
    payload = response.json()
    assert len(payload["data"]) == 2
