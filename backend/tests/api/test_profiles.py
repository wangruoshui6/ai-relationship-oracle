def test_get_my_profile_empty_allowed(client):
    client.post(
        "/api/v1/auth/register",
        json={"email": "profile@example.com", "password": "password123"},
    )
    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "profile@example.com", "password": "password123"},
    )
    token = login_response.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/v1/profiles/me", headers=headers)

    assert response.status_code == 200
    payload = response.json()
    assert payload["code"] == 0
    assert payload["data"] is None


def test_upsert_my_profile(client):
    client.post(
        "/api/v1/auth/register",
        json={"email": "profile@example.com", "password": "password123"},
    )
    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "profile@example.com", "password": "password123"},
    )
    token = login_response.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    response = client.put(
        "/api/v1/profiles/me",
        headers=headers,
        json={
            "gender": "male",
            "birth_date": "1998-05-01",
            "birth_time": "15:30:00",
            "birth_city": "Beijing",
            "birth_country": "China",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["code"] == 0
    assert payload["data"]["gender"] == "male"
    assert payload["data"]["birth_city"] == "Beijing"
    # With real Bazi computation, chart has day_master instead of status stub
    chart = payload["data"]["bazi_chart"]
    assert chart is not None
    assert "day_master" in chart
    assert "pillars" in chart


def test_upsert_my_profile_updates_existing_record(client):
    client.post(
        "/api/v1/auth/register",
        json={"email": "profile@example.com", "password": "password123"},
    )
    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "profile@example.com", "password": "password123"},
    )
    token = login_response.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    client.put(
        "/api/v1/profiles/me",
        headers=headers,
        json={
            "gender": "male",
            "birth_city": "Beijing",
        },
    )

    response = client.put(
        "/api/v1/profiles/me",
        headers=headers,
        json={
            "birth_city": "Shanghai",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["data"]["birth_city"] == "Shanghai"
