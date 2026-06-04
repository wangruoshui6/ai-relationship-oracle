def register_user(client, email: str = "user@example.com", password: str = "password123"):
    return client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": password,
        },
    )


def login_user(client, email: str = "user@example.com", password: str = "password123"):
    return client.post(
        "/api/v1/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )


def test_register_success(client):
    response = register_user(client)

    assert response.status_code == 201
    payload = response.json()
    assert payload["code"] == 0
    assert payload["data"]["email"] == "user@example.com"
    assert payload["data"]["status"] == "active"


def test_register_duplicate_email(client):
    register_user(client)
    response = register_user(client)

    assert response.status_code == 409
    payload = response.json()
    assert payload["code"] == 1005


def test_login_success(client):
    register_user(client)
    response = login_user(client)

    assert response.status_code == 200
    payload = response.json()
    assert payload["code"] == 0
    assert payload["data"]["access_token"]
    assert payload["data"]["token_type"] == "bearer"


def test_token_login_success(client):
    register_user(client)
    response = client.post(
        "/api/v1/auth/token",
        data={
            "username": "user@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["access_token"]
    assert payload["token_type"] == "bearer"


def test_login_invalid_password(client):
    register_user(client)
    response = login_user(client, password="wrong-pass")

    assert response.status_code == 401
    payload = response.json()
    assert payload["code"] == 1002


def test_me_requires_auth(client):
    response = client.get("/api/v1/auth/me")

    assert response.status_code == 401


def test_me_success(client):
    register_user(client)
    login_response = login_user(client)
    token = login_response.json()["data"]["access_token"]

    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["code"] == 0
    assert payload["data"]["email"] == "user@example.com"
