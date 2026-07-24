def test_register_login_refresh_and_profile(client):
    registration = client.post(
        "/api/v1/auth/register",
        json={"email": "sage@example.com", "password": "correct-horse-battery-staple"},
    )
    assert registration.status_code == 201

    login = client.post(
        "/api/v1/auth/token",
        json={"email": "sage@example.com", "password": "correct-horse-battery-staple"},
    )
    assert login.status_code == 200
    tokens = login.json()
    assert tokens["access_token"]

    profile = client.get(
        "/api/v1/auth/me", headers={"Authorization": f"Bearer {tokens['access_token']}"}
    )
    assert profile.status_code == 200
    assert profile.json()["email"] == "sage@example.com"

    refresh = client.post("/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert refresh.status_code == 200
    assert refresh.json()["access_token"] != ""


def test_auth_rejects_invalid_password(client):
    response = client.post(
        "/api/v1/auth/token",
        json={"email": "nobody@example.com", "password": "wrong-password-long-enough"},
    )
    assert response.status_code == 401
