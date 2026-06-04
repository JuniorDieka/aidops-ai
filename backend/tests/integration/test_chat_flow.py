import pytest
from fastapi.testclient import TestClient


class TestChatFlow:
    def test_health_endpoint(self, client: TestClient):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "version" in data
        assert "demo_mode" in data

    def test_root_endpoint(self, client: TestClient):
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "AidOps AI"
        assert "version" in data
        assert "demo_mode" in data
