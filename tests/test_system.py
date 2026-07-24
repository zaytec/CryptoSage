def test_health_and_metrics_are_exposed(client):
    assert client.get("/health/live").json() == {"status": "ok"}
    assert client.get("/health/ready").status_code == 200
    assert client.get("/metrics").status_code == 200


def test_market_websocket_stream_handles_ping(client):
    with client.websocket_connect("/ws/market/usd") as websocket:
        assert websocket.receive_json()["type"] == "market.update"
        websocket.send_text("ping")
        assert websocket.receive_json() == {"type": "pong"}
