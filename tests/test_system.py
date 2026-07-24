def test_health_and_metrics_are_exposed(client):
    assert client.get("/health/live").json() == {"status": "ok"}
    assert client.get("/health/ready").status_code == 200
    assert client.get("/metrics").status_code == 200
