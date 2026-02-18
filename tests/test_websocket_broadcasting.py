"""
Tests for WebSocket ride request broadcasting.

Tests cover:
- Broadcasting ride requests to connected drivers via WebSocket
- Notification content completeness
- WebSocket integration with matching service
"""
import pytest
from uuid import uuid4
from fastapi.testclient import TestClient
from app.main import app
from app.services.matching_service import MatchingService
from app.models.user import User, UserType, DriverProfile, DriverStatus
from app.models.ride import Ride, RideStatus, PaymentStatus
from datetime import datetime, timedelta
from app.utils.jwt import create_access_token


@pytest.fixture
def driver_with_websocket(db_session):
    """Create a driver and return token for WebSocket connection."""
    driver_id = str(uuid4())
    driver = User(
        user_id=driver_id,
        phone_number=f"+91{uuid4().hex[:10]}",
        phone_verified=True,
        name="Test Driver",
        email=f"driver_{uuid4().hex[:8]}@test.com",
        user_type=UserType.DRIVER,
        password_hash="hashed_password"
    )
    
    driver_profile = DriverProfile(
        driver_id=driver_id,
        license_number="DL123456",
        license_verified=True,
        vehicle_registration="MH12AB1234",
        vehicle_make="Toyota",
        vehicle_model="Innova",
        vehicle_color="White",
        vehicle_verified=True,
        insurance_expiry=datetime.utcnow() + timedelta(days=90),
        status=DriverStatus.AVAILABLE
    )
    
    driver.driver_profile = driver_profile
    db_session.add(driver)
    db_session.commit()
    
    token = create_access_token(driver_id, "driver", True)
    return driver, token


def test_websocket_ride_request_notification(redis_client, db_session, driver_with_websocket):
    """Test that ride request is sent via WebSocket to connected drivers."""
    driver, token = driver_with_websocket
    client = TestClient(app)
    
    # Connect driver via WebSocket
    with client.websocket_connect(f"/ws?token={token}") as websocket:
        # Receive connection confirmation
        conn_msg = websocket.receive_json()
        assert conn_msg["type"] == "connection_established"
        
        # Set driver as available with location
        matching_service = MatchingService(redis_client, db_session)
        matching_service.set_driver_available(
            driver.user_id,
            22.7196,
            75.8577
        )
        
        # Broadcast a ride request
        result = matching_service.broadcast_ride_request(
            ride_id="ride123",
            pickup_latitude=22.7196,
            pickup_longitude=75.8577,
            destination_latitude=22.7532,
            destination_longitude=75.8937,
            estimated_fare=120.0,
            radius_km=5.0
        )
        
        assert result["status"] == "success"
        assert result["drivers_notified"] == 1
        
        # Driver should receive WebSocket notification
        notification = websocket.receive_json()
        assert notification["type"] == "ride_request"
        assert notification["data"]["ride_id"] == "ride123"
        assert notification["data"]["pickup"]["latitude"] == 22.7196
        assert notification["data"]["pickup"]["longitude"] == 75.8577
        assert notification["data"]["destination"]["latitude"] == 22.7532
        assert notification["data"]["destination"]["longitude"] == 75.8937
        assert notification["data"]["estimated_fare"] == 120.0
        assert "distance_to_pickup_km" in notification["data"]
        assert "broadcast_time" in notification["data"]
        assert "timestamp" in notification


def test_websocket_notification_content_completeness(redis_client, db_session, driver_with_websocket):
    """Test that WebSocket notification includes all required fields (Property 12)."""
    driver, token = driver_with_websocket
    client = TestClient(app)
    
    with client.websocket_connect(f"/ws?token={token}") as websocket:
        # Receive connection confirmation
        websocket.receive_json()
        
        # Set driver as available
        matching_service = MatchingService(redis_client, db_session)
        matching_service.set_driver_available(
            driver.user_id,
            22.7196,
            75.8577
        )
        
        # Broadcast ride request
        matching_service.broadcast_ride_request(
            ride_id="ride456",
            pickup_latitude=22.7200,
            pickup_longitude=75.8600,
            destination_latitude=22.7500,
            destination_longitude=75.8900,
            estimated_fare=150.0,
            radius_km=5.0
        )
        
        # Receive notification
        notification = websocket.receive_json()
        
        # Verify all required fields are present
        assert notification["type"] == "ride_request"
        assert "data" in notification
        
        data = notification["data"]
        # Pickup location
        assert "pickup" in data
        assert "latitude" in data["pickup"]
        assert "longitude" in data["pickup"]
        
        # Destination
        assert "destination" in data
        assert "latitude" in data["destination"]
        assert "longitude" in data["destination"]
        
        # Estimated fare
        assert "estimated_fare" in data
        assert data["estimated_fare"] == 150.0
        
        # Additional useful information
        assert "distance_to_pickup_km" in data
        assert "broadcast_time" in data
        assert "timestamp" in notification


def test_multiple_drivers_receive_websocket_notifications(redis_client, db_session):
    """Test that multiple connected drivers receive ride request notifications."""
    client = TestClient(app)
    matching_service = MatchingService(redis_client, db_session)
    
    # Create multiple drivers
    drivers_and_tokens = []
    for i in range(3):
        driver_id = str(uuid4())
        driver = User(
            user_id=driver_id,
            phone_number=f"+91{uuid4().hex[:10]}",
            phone_verified=True,
            name=f"Driver {i}",
            email=f"driver{i}_{uuid4().hex[:8]}@test.com",
            user_type=UserType.DRIVER,
            password_hash="hashed_password"
        )
        
        driver_profile = DriverProfile(
            driver_id=driver_id,
            license_number=f"DL{i}23456",
            license_verified=True,
            vehicle_registration=f"MH12AB{i}234",
            vehicle_make="Toyota",
            vehicle_model="Innova",
            vehicle_color="White",
            vehicle_verified=True,
            insurance_expiry=datetime.utcnow() + timedelta(days=90),
            status=DriverStatus.AVAILABLE
        )
        
        driver.driver_profile = driver_profile
        db_session.add(driver)
        db_session.commit()
        
        token = create_access_token(driver_id, "driver", True)
        drivers_and_tokens.append((driver, token))
    
    # Connect all drivers via WebSocket
    websockets = []
    for driver, token in drivers_and_tokens:
        ws = client.websocket_connect(f"/ws?token={token}")
        websocket = ws.__enter__()
        websocket.receive_json()  # Connection confirmation
        websockets.append((driver, websocket, ws))
        
        # Set driver as available
        matching_service.set_driver_available(
            driver.user_id,
            22.7196 + (0.001 * len(websockets)),  # Slightly different locations
            75.8577
        )
    
    try:
        # Broadcast ride request
        result = matching_service.broadcast_ride_request(
            ride_id="ride789",
            pickup_latitude=22.7196,
            pickup_longitude=75.8577,
            destination_latitude=22.7532,
            destination_longitude=75.8937,
            estimated_fare=100.0,
            radius_km=5.0
        )
        
        assert result["drivers_notified"] == 3
        
        # All drivers should receive the notification
        for driver, websocket, _ in websockets:
            notification = websocket.receive_json()
            assert notification["type"] == "ride_request"
            assert notification["data"]["ride_id"] == "ride789"
    
    finally:
        # Clean up WebSocket connections
        for _, _, ws_context in websockets:
            ws_context.__exit__(None, None, None)


def test_disconnected_driver_does_not_receive_websocket(redis_client, db_session, driver_with_websocket):
    """Test that disconnected drivers don't receive WebSocket notifications."""
    driver, token = driver_with_websocket
    client = TestClient(app)
    matching_service = MatchingService(redis_client, db_session)
    
    # Set driver as available
    matching_service.set_driver_available(
        driver.user_id,
        22.7196,
        75.8577
    )
    
    # Broadcast ride request (driver not connected)
    result = matching_service.broadcast_ride_request(
        ride_id="ride999",
        pickup_latitude=22.7196,
        pickup_longitude=75.8577,
        destination_latitude=22.7532,
        destination_longitude=75.8937,
        estimated_fare=100.0,
        radius_km=5.0
    )
    
    # Driver is notified via Redis but not via WebSocket
    assert result["drivers_notified"] == 1
    # WebSocket count will be 0 since driver is not connected
    assert result["websocket_notifications_sent"] == 0


def test_websocket_notification_with_distance_info(redis_client, db_session, driver_with_websocket):
    """Test that WebSocket notification includes distance to pickup."""
    driver, token = driver_with_websocket
    client = TestClient(app)
    
    with client.websocket_connect(f"/ws?token={token}") as websocket:
        websocket.receive_json()  # Connection confirmation
        
        matching_service = MatchingService(redis_client, db_session)
        
        # Set driver at a specific location
        driver_lat, driver_lon = 22.7196, 75.8577
        matching_service.set_driver_available(
            driver.user_id,
            driver_lat,
            driver_lon
        )
        
        # Broadcast ride request from same location
        matching_service.broadcast_ride_request(
            ride_id="ride_nearby",
            pickup_latitude=driver_lat,
            pickup_longitude=driver_lon,
            destination_latitude=22.7532,
            destination_longitude=75.8937,
            estimated_fare=100.0,
            radius_km=5.0
        )
        
        notification = websocket.receive_json()
        
        # Distance should be very small (same location)
        assert notification["data"]["distance_to_pickup_km"] < 0.1
