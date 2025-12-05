"""Tests for health endpoint."""

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoint():
    """Test that health endpoint returns status."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["healthy", "degraded", "unhealthy"]
    assert "features" in data
    assert "enable_asr" in data["features"]
    assert "enable_llm" in data["features"]
    assert "services" in data
    assert "uptime_seconds" in data
    assert "timestamp" in data


def test_liveness_probe():
    """Test Kubernetes liveness probe."""
    response = client.get("/health/live")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "alive"


def test_readiness_probe():
    """Test Kubernetes readiness probe."""
    response = client.get("/health/ready")
    # May be 200 or 503 depending on DB connectivity
    assert response.status_code in [200, 503]
