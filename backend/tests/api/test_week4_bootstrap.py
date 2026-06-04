def build_auth_headers(client, email: str = "week4@example.com"):
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


def test_first_consultation_auto_creates_partner_and_memory(client):
    headers = build_auth_headers(client)
    response = client.post(
        "/api/v1/consultations",
        headers=headers,
        json={
            "message": "我和 Sarah 分手三个月了，最近她点赞我朋友圈，她会回来吗？",
            "analysis_methods": ["bazi", "psychology"],
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["code"] == 0
    assert payload["data"]["conversation_id"]
    assert payload["data"]["partner_id"]
    assert payload["data"]["auto_created_partner"] is True
    assert payload["data"]["memory_updated"] is True
