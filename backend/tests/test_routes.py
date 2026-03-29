import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch

@pytest.fixture
def client():
    with patch("app.db.database.init_db", new_callable=AsyncMock):
        from app.main import app
        return TestClient(app)

def test_health(client):
    with patch("app.api.health.httpx.AsyncClient"), \
         patch("app.api.health.aiosqlite.connect"), \
         patch("app.api.health.get_collection_count", new_callable=AsyncMock, return_value=0):
        assert client.get("/api/health").status_code == 200

def test_ingest_status(client):
    r = client.get("/api/ingest/status")
    assert r.status_code==200 and "running" in r.json()

def test_no_key(client):    assert client.post("/api/ingest", json={}).status_code == 422
def test_wrong_key(client): assert client.post("/api/ingest", json={}, headers={"X-API-Key":"bad"}).status_code == 401
