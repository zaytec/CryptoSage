from datetime import UTC, datetime


def auth_headers(client):
    client.post(
        "/api/v1/auth/register",
        json={"email": "portfolio@example.com", "password": "correct-horse-battery-staple"},
    )
    token = client.post(
        "/api/v1/auth/token",
        json={"email": "portfolio@example.com", "password": "correct-horse-battery-staple"},
    ).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_portfolio_transaction_requires_owner_and_persists(client):
    headers = auth_headers(client)
    created = client.post("/api/v1/portfolios", headers=headers, json={"name": "Long-term"})
    assert created.status_code == 201
    portfolio_id = created.json()["id"]
    transaction = client.post(
        f"/api/v1/portfolios/{portfolio_id}/transactions",
        headers=headers,
        json={
            "coin_id": "bitcoin",
            "symbol": "btc",
            "transaction_type": "buy",
            "quantity": "0.5",
            "price": "50000",
            "fees": "10",
            "occurred_at": datetime.now(UTC).isoformat(),
        },
    )
    assert transaction.status_code == 201
    assert client.get("/api/v1/portfolios", headers=headers).json()[0]["name"] == "Long-term"
    analytics = client.get(f"/api/v1/portfolios/{portfolio_id}/analytics", headers=headers)
    assert analytics.status_code == 200
    assert float(analytics.json()["total_market_value"]) == 30000
    assert float(analytics.json()["unrealized_pnl"]) == 4990


def test_unknown_portfolio_is_not_disclosed(client):
    headers = auth_headers(client)
    response = client.get(
        "/api/v1/portfolios/00000000-0000-0000-0000-000000000000/analytics", headers=headers
    )
    assert response.status_code == 404
