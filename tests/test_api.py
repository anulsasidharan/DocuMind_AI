"""API smoke tests."""

from fastapi.testclient import TestClient


def test_health():
    from api.main import app

    client = TestClient(app)
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"
