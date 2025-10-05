from fastapi.testclient import TestClient
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from visualization.fastapi_app import app
  # Change 'main' to your actual FastAPI filename if it's not 'main.py'

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_trade_signals_endpoint():
    response = client.get("/trade_signals")
    assert response.status_code == 200
    assert "signals" in response.json()
