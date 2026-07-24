def test_market_endpoints_are_cached_and_historical_data_is_available(client):
    first = client.get("/api/v1/market/coins?limit=1")
    second = client.get("/api/v1/market/coins?limit=1")
    assert first.status_code == second.status_code == 200
    assert first.json()[0]["id"] == "bitcoin"
    assert client.get("/api/v1/market/trending").json()[0]["item"]["id"] == "bitcoin"
    assert client.get("/api/v1/market/coins/bitcoin/history?days=7").json()["days"] == 7
    statistics = client.get("/api/v1/market/cache-statistics").json()
    assert statistics["hits"] >= 1
