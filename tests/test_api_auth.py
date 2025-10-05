import pytest
from fastapi.testclient import TestClient
import os
from visualization.fastapi_app import app

@pytest.fixture
def client():
    return TestClient(app)

def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200

def test_metrics_requires_token(monkeypatch, client):
    monkeypatch.setenv("DASH_API_TOKEN", "secret")
    r = client.get("/metrics")
    assert r.status_code in (401, 422)  # missing header or unauthorized
    r2 = client.get("/metrics", headers={"x-api-token": "secret"})
    assert r2.status_code == 200
