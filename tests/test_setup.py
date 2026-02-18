"""
Basic tests to verify project setup is correct.
"""
import pytest
from app.config import settings


def test_settings_loaded():
    """Test that settings are loaded correctly."""
    assert settings.app_name is not None
    assert settings.base_fare == 30.0
    assert settings.per_km_rate == 12.0


def test_health_endpoint(client):
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_root_endpoint(client):
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
