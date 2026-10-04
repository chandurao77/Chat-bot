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

@pytest.fixture
def ingest_mock():
    with patch("app.api.routes.ingest.ingest_confluence", new_callable=AsyncMock) as m:
        yield m

def test_ingest_requires_key_when_configured(client, ingest_mock):
    with patch("app.config.settings.api_key", "secret"):
        assert client.post("/api/ingest", json={}).status_code == 401
    ingest_mock.assert_not_called()

def test_ingest_rejects_wrong_key(client, ingest_mock):
    with patch("app.config.settings.api_key", "secret"):
        r = client.post("/api/ingest", json={}, headers={"X-API-Key": "bad"})
    assert r.status_code == 401
    ingest_mock.assert_not_called()

def test_ingest_accepts_right_key(client, ingest_mock):
    with patch("app.config.settings.api_key", "secret"):
        r = client.post("/api/ingest", json={}, headers={"X-API-Key": "secret"})
    assert r.status_code == 202
    ingest_mock.assert_called_once()

def test_ingest_open_when_no_key_configured(client, ingest_mock):
    with patch("app.config.settings.api_key", ""):
        assert client.post("/api/ingest", json={}).status_code == 202

def test_ingest_rejects_malformed_body(client, ingest_mock):
    with patch("app.config.settings.api_key", ""):
        assert client.post("/api/ingest", json={"spaces": "DEV"}).status_code == 422
