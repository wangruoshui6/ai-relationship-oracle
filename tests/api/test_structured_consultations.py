def build_auth_headers(client, email: str = "structured@example.com"):
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


def test_structured_consultation_with_solar_and_lunar_profiles(client):
    headers = build_auth_headers(client)
    response = client.post(
        "/api/v1/structured-consultations",
        headers=headers,
        json={
            "user_profile": {
                "gender": "male",
                "calendar_type": "solar",
                "birth_date": "2005-08-25",
                "birth_time": "10:20:00",
                "birth_city": "Tangshan",
                "birth_country": "China"
            },
            "partner_profile": {
                "nickname": "她",
                "gender": "female",
                "relationship_type": "unknown",
                "calendar_type": "lunar",
                "birth_date": "2007-01-27",
                "birth_time": "02:05:00",
                "birth_city": "Shijiazhuang",
                "birth_country": "China"
            },
            "question": "我们现在分开了，还能复合吗？",
            "analysis_methods": ["bazi", "psychology"]
        },
    )

    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["conversation_id"]
    assert payload["partner_id"]
    assert payload["user_profile"]["calendar_type"] == "solar"
    assert payload["partner_profile"]["calendar_type"] == "lunar"
    assert payload["partner_profile"]["lunar_birth_date"] == "2007-01-27"
    assert payload["normalized_dates"]["partner_birth_date"] != "2007-01-27"
    assert payload["bazi_ready"]["user"] is True
    assert payload["bazi_ready"]["partner"] is True
    assert payload["answer"]


def test_structured_consultation_stream_returns_sse_events(client):
    headers = build_auth_headers(client, email="structured-stream@example.com")
    response = client.post(
        "/api/v1/structured-consultations/stream",
        headers=headers,
        json={
            "user_profile": {
                "gender": "male",
                "calendar_type": "solar",
                "birth_date": "2005-08-25",
                "birth_time": "10:20:00",
                "birth_city": "Tangshan",
                "birth_country": "China"
            },
            "partner_profile": {
                "nickname": "她",
                "gender": "female",
                "relationship_type": "unknown",
                "calendar_type": "lunar",
                "birth_date": "2007-01-27",
                "birth_time": "02:05:00",
                "birth_city": "Shijiazhuang",
                "birth_country": "China"
            },
            "question": "我们现在分开了，还能复合吗？",
            "analysis_methods": ["bazi", "psychology"]
        },
    )

    assert response.status_code == 200
    assert "text/event-stream" in response.headers["content-type"]
    assert "event: status" in response.text
    assert "event: done" in response.text
