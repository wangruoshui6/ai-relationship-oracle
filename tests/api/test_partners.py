def build_auth_headers(client, email: str = "partner@example.com"):
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


def create_partner(client, headers, nickname: str = "Sarah"):
    return client.post(
        "/api/v1/partners",
        headers=headers,
        json={
            "nickname": nickname,
            "gender": "female",
            "relationship_type": "ex",
            "birth_date": "1999-03-10",
            "birth_city": "London",
            "birth_country": "UK",
        },
    )


def test_create_partner(client):
    headers = build_auth_headers(client)
    response = create_partner(client, headers)

    assert response.status_code == 200
    payload = response.json()
    assert payload["code"] == 0
    assert payload["data"]["nickname"] == "Sarah"
    assert payload["data"]["relationship_type"] == "ex"


def test_create_partner_with_lunar_birth_date(client):
    headers = build_auth_headers(client, email="partner-lunar@example.com")
    response = client.post(
        "/api/v1/partners",
        headers=headers,
        json={
            "nickname": "Lunar Sarah",
            "gender": "female",
            "relationship_type": "ex",
            "birth_date": "2007-01-27",
            "birth_time": "02:05:00",
            "birth_city": "Shijiazhuang",
            "birth_country": "China",
            "calendar_type": "lunar",
        },
    )

    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["calendar_type"] == "lunar"
    assert payload["lunar_birth_date"] == "2007-01-27"
    assert payload["birth_date"] != "2007-01-27"


def test_list_partners(client):
    headers = build_auth_headers(client)
    create_partner(client, headers, nickname="Sarah")
    create_partner(client, headers, nickname="Amy")

    response = client.get("/api/v1/partners", headers=headers)

    assert response.status_code == 200
    payload = response.json()
    assert len(payload["data"]) == 2


def test_update_partner(client):
    headers = build_auth_headers(client)
    created = create_partner(client, headers)
    partner_id = created.json()["data"]["id"]

    response = client.put(
        f"/api/v1/partners/{partner_id}",
        headers=headers,
        json={
            "nickname": "Sarah Updated",
            "relationship_type": "current",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["data"]["nickname"] == "Sarah Updated"
    assert payload["data"]["relationship_type"] == "current"


def test_delete_partner(client):
    headers = build_auth_headers(client)
    created = create_partner(client, headers)
    partner_id = created.json()["data"]["id"]

    delete_response = client.delete(f"/api/v1/partners/{partner_id}", headers=headers)
    assert delete_response.status_code == 200
    assert delete_response.json()["data"]["deleted"] is True

    get_response = client.get(f"/api/v1/partners/{partner_id}", headers=headers)
    assert get_response.status_code == 404


def test_partner_access_isolated_by_user(client):
    headers_a = build_auth_headers(client, email="owner@example.com")
    created = create_partner(client, headers_a)
    partner_id = created.json()["data"]["id"]

    headers_b = build_auth_headers(client, email="other@example.com")
    response = client.get(f"/api/v1/partners/{partner_id}", headers=headers_b)

    assert response.status_code == 404
