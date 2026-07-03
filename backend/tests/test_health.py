"""Smoke tests: the app boots and basic endpoints respond."""


def test_root(client):
    resp = client.get("/")
    assert resp.status_code == 200
    body = resp.json()
    assert body["app"] == "CEO Tracker"
    assert body["status"] == "running"


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "healthy"}
