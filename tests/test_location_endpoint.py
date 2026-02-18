"""
Tests for location API endpoints.
Tests driver location tracking endpoints.

Requirements: 4.4, 8.1, 8.2
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from app.main import app
from app.models.location import Location
from app.routers.location import get_current_user


class TestDriverLocationUpdate:
    """Test POST /api/location/driver endpoint."""
    
    def test_update_driver_location_success(self):
        """Test successful driver location update."""
        # Override authentication dependency
        async def override_get_current_user():
            return {
                "user_id": "driver123",
                "user_type": "driver",
                "email": "driver@test.com"
            }
        
        app.dependency_overrides[get_current_user] = override_get_current_user
        
        # Mock LocationService
        with patch('app.routers.location.LocationService') as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            
            # Mock validation
            mock_service.validate_location_boundaries.return_value = {
                "valid": True,
                "message": "Location is within service area",
                "latitude": 22.7196,
                "longitude": 75.8577
            }
            
            # Mock location update
            mock_location = Location.from_lat_lon(
                user_id="driver123",
                user_type="driver",
                latitude=22.7196,
                longitude=75.8577,
                address="Vijay Nagar, Indore",
                status="available",
                accuracy=10.5,
                timestamp=datetime.now()
            )
            
            async def mock_update(*args, **kwargs):
                return mock_location
            
            mock_service.update_driver_location = mock_update
            
            # Make request
            client = TestClient(app)
            response = client.post(
                "/api/location/driver",
                json={
                    "latitude": 22.7196,
                    "longitude": 75.8577,
                    "address": "Vijay Nagar, Indore",
                    "status": "available",
                    "accuracy": 10.5
                }
            )
            
            # Assertions
            assert response.status_code == 200
            data = response.json()
            assert data["user_id"] == "driver123"
            assert data["latitude"] == 22.7196
            assert data["longitude"] == 75.8577
            assert data["address"] == "Vijay Nagar, Indore"
            assert data["status"] == "available"
            assert data["message"] == "Location updated successfully"
        
        # Clean up
        app.dependency_overrides.clear()
    
    def test_update_location_non_driver_forbidden(self):
        """Test that non-drivers cannot update location."""
        # Override authentication to return a rider
        async def override_get_current_user():
            return {
                "user_id": "rider123",
                "user_type": "rider",
                "email": "rider@test.com"
            }
        
        app.dependency_overrides[get_current_user] = override_get_current_user
        
        client = TestClient(app)
        response = client.post(
            "/api/location/driver",
            json={
                "latitude": 22.7196,
                "longitude": 75.8577
            }
        )
        
        assert response.status_code == 403
        assert "Only drivers can update location" in response.json()["detail"]
        
        # Clean up
        app.dependency_overrides.clear()
    
    def test_update_location_outside_service_area(self):
        """Test that locations outside service area are rejected."""
        # Override authentication
        async def override_get_current_user():
            return {
                "user_id": "driver123",
                "user_type": "driver",
                "email": "driver@test.com"
            }
        
        app.dependency_overrides[get_current_user] = override_get_current_user
        
        # Mock LocationService
        with patch('app.routers.location.LocationService') as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            
            # Mock validation to return invalid
            mock_service.validate_location_boundaries.return_value = {
                "valid": False,
                "message": "Location is outside Indore service area",
                "latitude": 28.6139,
                "longitude": 77.2090
            }
            
            client = TestClient(app)
            response = client.post(
                "/api/location/driver",
                json={
                    "latitude": 28.6139,  # Delhi coordinates
                    "longitude": 77.2090
                }
            )
            
            assert response.status_code == 400
            assert "outside Indore service area" in response.json()["detail"]
        
        # Clean up
        app.dependency_overrides.clear()


class TestGetDriverLocation:
    """Test GET /api/location/driver/{driver_id} endpoint."""
    
    def test_get_driver_location_success(self):
        """Test successful retrieval of driver location."""
        # Override authentication
        async def override_get_current_user():
            return {
                "user_id": "rider123",
                "user_type": "rider",
                "email": "rider@test.com"
            }
        
        app.dependency_overrides[get_current_user] = override_get_current_user
        
        # Mock LocationService
        with patch('app.routers.location.LocationService') as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            
            mock_location = Location.from_lat_lon(
                user_id="driver123",
                user_type="driver",
                latitude=22.7196,
                longitude=75.8577,
                address="Vijay Nagar, Indore",
                status="available",
                timestamp=datetime.now()
            )
            
            async def mock_get(*args, **kwargs):
                return mock_location
            
            mock_service.get_driver_location = mock_get
            
            client = TestClient(app)
            response = client.get("/api/location/driver/driver123")
            
            assert response.status_code == 200
            data = response.json()
            assert data["user_id"] == "driver123"
            assert data["latitude"] == 22.7196
            assert data["longitude"] == 75.8577
            assert data["message"] == "Location retrieved successfully"
        
        # Clean up
        app.dependency_overrides.clear()
    
    def test_get_driver_location_not_found(self):
        """Test getting location for driver with no location data."""
        # Override authentication
        async def override_get_current_user():
            return {
                "user_id": "rider123",
                "user_type": "rider",
                "email": "rider@test.com"
            }
        
        app.dependency_overrides[get_current_user] = override_get_current_user
        
        # Mock LocationService
        with patch('app.routers.location.LocationService') as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            
            async def mock_get(*args, **kwargs):
                return None
            
            mock_service.get_driver_location = mock_get
            
            client = TestClient(app)
            response = client.get("/api/location/driver/driver999")
            
            assert response.status_code == 404
            assert "Location not found" in response.json()["detail"]
        
        # Clean up
        app.dependency_overrides.clear()


class TestValidateLocation:
    """Test POST /api/location/validate endpoint."""
    
    def test_validate_location_within_service_area(self):
        """Test validation of location within service area."""
        # Mock LocationService
        with patch('app.routers.location.LocationService') as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            
            mock_service.validate_location_boundaries.return_value = {
                "valid": True,
                "message": "Location is within service area",
                "latitude": 22.7196,
                "longitude": 75.8577
            }
            
            client = TestClient(app)
            response = client.post(
                "/api/location/validate",
                params={
                    "latitude": 22.7196,
                    "longitude": 75.8577
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["valid"] is True
            assert "within service area" in data["message"]
    
    def test_validate_location_outside_service_area(self):
        """Test validation of location outside service area."""
        # Mock LocationService
        with patch('app.routers.location.LocationService') as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            
            mock_service.validate_location_boundaries.return_value = {
                "valid": False,
                "message": "Location is outside Indore service area",
                "latitude": 28.6139,
                "longitude": 77.2090
            }
            
            client = TestClient(app)
            response = client.post(
                "/api/location/validate",
                params={
                    "latitude": 28.6139,
                    "longitude": 77.2090
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["valid"] is False
            assert "outside" in data["message"]

