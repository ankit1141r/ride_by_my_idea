"""
Tests for real-time location updates via WebSocket.

Tests Requirements 8.1, 8.2, 8.4
"""
import pytest
from fastapi.testclient import TestClient
from fastapi import WebSocket
from datetime import datetime
import json
from unittest.mock import AsyncMock, MagicMock, patch
from app.main import app
from app.models.user import User, DriverProfile
from app.models.ride import Ride, RideStatus
from app.utils.jwt import create_access_token
from app.services.websocket_service import connection_manager


@pytest.fixture
def rider_user(db_session):
    """Create a test rider user."""
    user = User(
        user_id="rider123",
        phone_number="+919876543210",
        phone_verified=True,
        name="Test Rider",
        email="rider@test.com",
        user_type="rider",
        password_hash="hashed_password"
    )
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def driver_user(db_session):
    """Create a test driver user."""
    from datetime import timedelta
    
    user = User(
        user_id="driver123",
        phone_number="+919876543211",
        phone_verified=True,
        name="Test Driver",
        email="driver@test.com",
        user_type="driver",
        password_hash="hashed_password"
    )
    db_session.add(user)
    
    profile = DriverProfile(
        driver_id="driver123",
        license_number="DL1234567890",
        license_verified=True,
        vehicle_registration="MP09AB1234",
        vehicle_make="Toyota",
        vehicle_model="Innova",
        vehicle_color="White",
        vehicle_verified=True,
        insurance_expiry=datetime.utcnow() + timedelta(days=90),
        status="available"
    )
    db_session.add(profile)
    db_session.commit()
    return user


@pytest.fixture
def active_ride(db_session, rider_user, driver_user):
    """Create an active ride."""
    ride = Ride(
        ride_id="ride123",
        rider_id=rider_user.user_id,
        driver_id=driver_user.user_id,
        status=RideStatus.DRIVER_ARRIVING,
        pickup_location={
            "latitude": 22.7196,
            "longitude": 75.8577,
            "address": "Rajwada, Indore"
        },
        destination={
            "latitude": 22.7532,
            "longitude": 75.8937,
            "address": "Vijay Nagar, Indore"
        },
        estimated_fare=120.0,
        fare_breakdown={
            "base_fare": 30.0,
            "distance_charge": 90.0,
            "surge_multiplier": 1.0
        },
        requested_at=datetime.utcnow(),
        matched_at=datetime.utcnow()
    )
    db_session.add(ride)
    db_session.commit()
    return ride


@pytest.fixture
def driver_token(driver_user):
    """Create JWT token for driver."""
    return create_access_token(
        user_id=driver_user.user_id,
        user_type=driver_user.user_type,
        phone_verified=driver_user.phone_verified
    )


@pytest.fixture
def rider_token(rider_user):
    """Create JWT token for rider."""
    return create_access_token(
        user_id=rider_user.user_id,
        user_type=rider_user.user_type,
        phone_verified=rider_user.phone_verified
    )


@pytest.mark.asyncio
async def test_driver_location_update_stored_in_mongodb(driver_user, driver_token):
    """
    Test that driver location updates are stored in MongoDB.
    
    Requirements: 8.1, 8.2
    """
    # Mock MongoDB location service
    mock_location = MagicMock()
    mock_location.timestamp = datetime.utcnow()
    
    with patch('app.routers.websocket.get_mongodb') as mock_get_mongodb, \
         patch('app.routers.websocket.LocationService') as mock_location_service_class:
        
        mock_location_service = AsyncMock()
        mock_location_service.update_driver_location = AsyncMock(return_value=mock_location)
        mock_location_service_class.return_value = mock_location_service
        
        # Create WebSocket test client
        with TestClient(app).websocket_connect(f"/ws?token={driver_token}") as websocket:
            # Receive connection confirmation
            data = websocket.receive_json()
            assert data["type"] == "connection_established"
            
            # Send location update
            websocket.send_json({
                "type": "driver_location_update",
                "data": {
                    "latitude": 22.7196,
                    "longitude": 75.8577,
                    "accuracy": 10.0
                }
            })
            
            # Receive acknowledgment
            response = websocket.receive_json()
            assert response["type"] == "location_update_ack"
            assert response["data"]["received"] is True
            
            # Verify location was stored
            mock_location_service.update_driver_location.assert_called_once()
            call_args = mock_location_service.update_driver_location.call_args
            assert call_args[1]["driver_id"] == driver_user.user_id
            assert call_args[1]["latitude"] == 22.7196
            assert call_args[1]["longitude"] == 75.8577
            assert call_args[1]["accuracy"] == 10.0


@pytest.mark.asyncio
async def test_location_update_broadcast_to_rider(
    driver_user, rider_user, active_ride, driver_token, rider_token, db_session
):
    """
    Test that driver location updates are broadcast to matched rider.
    
    Requirements: 8.1, 8.2
    """
    # Mock MongoDB location service
    mock_location = MagicMock()
    mock_location.timestamp = datetime.utcnow()
    
    with patch('app.routers.websocket.get_mongodb') as mock_get_mongodb, \
         patch('app.routers.websocket.LocationService') as mock_location_service_class, \
         patch('app.routers.websocket.get_db') as mock_get_db:
        
        mock_location_service = AsyncMock()
        mock_location_service.update_driver_location = AsyncMock(return_value=mock_location)
        mock_location_service_class.return_value = mock_location_service
        
        # Mock database session
        mock_get_db.return_value = iter([db_session])
        
        # Connect rider first
        with TestClient(app).websocket_connect(f"/ws?token={rider_token}") as rider_ws:
            rider_data = rider_ws.receive_json()
            assert rider_data["type"] == "connection_established"
            
            # Connect driver
            with TestClient(app).websocket_connect(f"/ws?token={driver_token}") as driver_ws:
                driver_data = driver_ws.receive_json()
                assert driver_data["type"] == "connection_established"
                
                # Driver sends location update with ride_id
                driver_ws.send_json({
                    "type": "driver_location_update",
                    "data": {
                        "latitude": 22.7200,
                        "longitude": 75.8580,
                        "accuracy": 10.0,
                        "ride_id": active_ride.ride_id
                    }
                })
                
                # Driver receives acknowledgment
                driver_response = driver_ws.receive_json()
                assert driver_response["type"] == "location_update_ack"
                
                # Rider should receive location update
                rider_response = rider_ws.receive_json()
                assert rider_response["type"] == "driver_location_update"
                assert rider_response["data"]["ride_id"] == active_ride.ride_id
                assert rider_response["data"]["driver_id"] == driver_user.user_id
                assert rider_response["data"]["latitude"] == 22.7200
                assert rider_response["data"]["longitude"] == 75.8580


@pytest.mark.asyncio
async def test_location_update_without_ride_id(driver_user, driver_token):
    """
    Test that location updates without ride_id are stored but not broadcast.
    
    Requirements: 8.1
    """
    # Mock MongoDB location service
    mock_location = MagicMock()
    mock_location.timestamp = datetime.utcnow()
    
    with patch('app.routers.websocket.get_mongodb') as mock_get_mongodb, \
         patch('app.routers.websocket.LocationService') as mock_location_service_class:
        
        mock_location_service = AsyncMock()
        mock_location_service.update_driver_location = AsyncMock(return_value=mock_location)
        mock_location_service_class.return_value = mock_location_service
        
        with TestClient(app).websocket_connect(f"/ws?token={driver_token}") as websocket:
            # Receive connection confirmation
            data = websocket.receive_json()
            assert data["type"] == "connection_established"
            
            # Send location update without ride_id
            websocket.send_json({
                "type": "driver_location_update",
                "data": {
                    "latitude": 22.7196,
                    "longitude": 75.8577,
                    "accuracy": 10.0
                }
            })
            
            # Receive acknowledgment
            response = websocket.receive_json()
            assert response["type"] == "location_update_ack"
            assert response["data"]["received"] is True
            
            # Verify location was stored
            mock_location_service.update_driver_location.assert_called_once()


@pytest.mark.asyncio
async def test_proximity_notification_when_driver_nearby(
    driver_user, rider_user, active_ride, driver_token, rider_token, db_session
):
    """
    Test that proximity notification is sent when driver is within 500m of pickup.
    
    Requirements: 8.4
    """
    # Mock MongoDB location service
    mock_location = MagicMock()
    mock_location.timestamp = datetime.utcnow()
    
    with patch('app.routers.websocket.get_mongodb') as mock_get_mongodb, \
         patch('app.routers.websocket.LocationService') as mock_location_service_class, \
         patch('app.routers.websocket.get_db') as mock_get_db:
        
        mock_location_service = AsyncMock()
        mock_location_service.update_driver_location = AsyncMock(return_value=mock_location)
        mock_location_service_class.return_value = mock_location_service
        
        # Mock database session
        mock_get_db.return_value = iter([db_session])
        
        # Connect rider first
        with TestClient(app).websocket_connect(f"/ws?token={rider_token}") as rider_ws:
            rider_data = rider_ws.receive_json()
            assert rider_data["type"] == "connection_established"
            
            # Connect driver
            with TestClient(app).websocket_connect(f"/ws?token={driver_token}") as driver_ws:
                driver_data = driver_ws.receive_json()
                assert driver_data["type"] == "connection_established"
                
                # Driver sends location update very close to pickup (within 500m)
                # Pickup is at 22.7196, 75.8577
                # Send location at 22.7200, 75.8580 (approximately 50m away)
                driver_ws.send_json({
                    "type": "driver_location_update",
                    "data": {
                        "latitude": 22.7200,
                        "longitude": 75.8580,
                        "accuracy": 10.0,
                        "ride_id": active_ride.ride_id
                    }
                })
                
                # Driver receives acknowledgment
                driver_response = driver_ws.receive_json()
                assert driver_response["type"] == "location_update_ack"
                
                # Rider should receive location update
                rider_response = rider_ws.receive_json()
                assert rider_response["type"] == "driver_location_update"
                
                # Rider should also receive proximity notification
                proximity_response = rider_ws.receive_json()
                assert proximity_response["type"] == "driver_nearby"
                assert proximity_response["data"]["ride_id"] == active_ride.ride_id
                assert proximity_response["data"]["driver_id"] == driver_user.user_id
                assert proximity_response["data"]["distance_meters"] <= 500


@pytest.mark.asyncio
async def test_no_proximity_notification_when_driver_far(
    driver_user, rider_user, active_ride, driver_token, rider_token, db_session
):
    """
    Test that no proximity notification is sent when driver is far from pickup.
    
    Requirements: 8.4
    """
    # Mock MongoDB location service
    mock_location = MagicMock()
    mock_location.timestamp = datetime.utcnow()
    
    with patch('app.routers.websocket.get_mongodb') as mock_get_mongodb, \
         patch('app.routers.websocket.LocationService') as mock_location_service_class, \
         patch('app.routers.websocket.get_db') as mock_get_db:
        
        mock_location_service = AsyncMock()
        mock_location_service.update_driver_location = AsyncMock(return_value=mock_location)
        mock_location_service_class.return_value = mock_location_service
        
        # Mock database session
        mock_get_db.return_value = iter([db_session])
        
        # Connect rider first
        with TestClient(app).websocket_connect(f"/ws?token={rider_token}") as rider_ws:
            rider_data = rider_ws.receive_json()
            assert rider_data["type"] == "connection_established"
            
            # Connect driver
            with TestClient(app).websocket_connect(f"/ws?token={driver_token}") as driver_ws:
                driver_data = driver_ws.receive_json()
                assert driver_data["type"] == "connection_established"
                
                # Driver sends location update far from pickup (more than 500m)
                # Pickup is at 22.7196, 75.8577
                # Send location at 22.7300, 75.8700 (approximately 1.5km away)
                driver_ws.send_json({
                    "type": "driver_location_update",
                    "data": {
                        "latitude": 22.7300,
                        "longitude": 75.8700,
                        "accuracy": 10.0,
                        "ride_id": active_ride.ride_id
                    }
                })
                
                # Driver receives acknowledgment
                driver_response = driver_ws.receive_json()
                assert driver_response["type"] == "location_update_ack"
                
                # Rider should receive location update
                rider_response = rider_ws.receive_json()
                assert rider_response["type"] == "driver_location_update"
                
                # Rider should NOT receive proximity notification
                # (no more messages should be in the queue)


@pytest.mark.asyncio
async def test_location_update_missing_coordinates(driver_user, driver_token):
    """
    Test that location updates with missing coordinates are rejected.
    """
    with TestClient(app).websocket_connect(f"/ws?token={driver_token}") as websocket:
        # Receive connection confirmation
        data = websocket.receive_json()
        assert data["type"] == "connection_established"
        
        # Send location update without latitude
        websocket.send_json({
            "type": "driver_location_update",
            "data": {
                "longitude": 75.8577,
                "accuracy": 10.0
            }
        })
        
        # Receive error
        response = websocket.receive_json()
        assert response["type"] == "error"
        assert "latitude" in response["data"]["message"].lower()


@pytest.mark.asyncio
async def test_location_update_only_for_active_rides(
    driver_user, rider_user, driver_token, rider_token, db_session
):
    """
    Test that location updates are only broadcast for active rides.
    """
    # Create a completed ride (not active)
    completed_ride = Ride(
        ride_id="ride456",
        rider_id=rider_user.user_id,
        driver_id=driver_user.user_id,
        status=RideStatus.COMPLETED,
        pickup_location={
            "latitude": 22.7196,
            "longitude": 75.8577,
            "address": "Rajwada, Indore"
        },
        destination={
            "latitude": 22.7532,
            "longitude": 75.8937,
            "address": "Vijay Nagar, Indore"
        },
        estimated_fare=120.0,
        fare_breakdown={
            "base_fare": 30.0,
            "distance_charge": 90.0,
            "surge_multiplier": 1.0
        },
        requested_at=datetime.utcnow(),
        matched_at=datetime.utcnow(),
        completed_at=datetime.utcnow()
    )
    db_session.add(completed_ride)
    db_session.commit()
    
    # Mock MongoDB location service
    mock_location = MagicMock()
    mock_location.timestamp = datetime.utcnow()
    
    with patch('app.routers.websocket.get_mongodb') as mock_get_mongodb, \
         patch('app.routers.websocket.LocationService') as mock_location_service_class, \
         patch('app.routers.websocket.get_db') as mock_get_db:
        
        mock_location_service = AsyncMock()
        mock_location_service.update_driver_location = AsyncMock(return_value=mock_location)
        mock_location_service_class.return_value = mock_location_service
        
        # Mock database session
        mock_get_db.return_value = iter([db_session])
        
        # Connect rider first
        with TestClient(app).websocket_connect(f"/ws?token={rider_token}") as rider_ws:
            rider_data = rider_ws.receive_json()
            assert rider_data["type"] == "connection_established"
            
            # Connect driver
            with TestClient(app).websocket_connect(f"/ws?token={driver_token}") as driver_ws:
                driver_data = driver_ws.receive_json()
                assert driver_data["type"] == "connection_established"
                
                # Driver sends location update for completed ride
                driver_ws.send_json({
                    "type": "driver_location_update",
                    "data": {
                        "latitude": 22.7200,
                        "longitude": 75.8580,
                        "accuracy": 10.0,
                        "ride_id": completed_ride.ride_id
                    }
                })
                
                # Driver receives acknowledgment
                driver_response = driver_ws.receive_json()
                assert driver_response["type"] == "location_update_ack"
                
                # Rider should NOT receive location update for completed ride
                # (no messages should be in the queue)
