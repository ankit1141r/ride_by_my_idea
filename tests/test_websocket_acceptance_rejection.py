"""
Tests for driver acceptance/rejection via WebSocket.

Tests the WebSocket message handling for drivers accepting or rejecting
ride requests, including match confirmation and notification cancellation.
"""
import pytest
import json
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.models.user import User, DriverProfile
from app.models.ride import Ride, RideStatus
from app.services.matching_service import MatchingService
from app.services.websocket_service import connection_manager
from app.utils.jwt import create_access_token
import uuid


@pytest.fixture
def rider(db_session: Session):
    """Create a test rider."""
    rider = User(
        user_id=str(uuid.uuid4()),
        phone_number="+919876543210",
        phone_verified=True,
        name="Test Rider",
        email="rider@test.com",
        user_type="rider",
        password_hash="hashed_password"  # Add password hash
    )
    db_session.add(rider)
    db_session.commit()
    db_session.refresh(rider)
    return rider


@pytest.fixture
def driver1(db_session: Session):
    """Create first test driver."""
    driver = User(
        user_id=str(uuid.uuid4()),
        phone_number="+919876543211",
        phone_verified=True,
        name="Test Driver 1",
        email="driver1@test.com",
        user_type="driver",
        password_hash="hashed_password"  # Add password hash
    )
    db_session.add(driver)
    db_session.flush()
    
    driver_profile = DriverProfile(
        driver_id=driver.user_id,
        license_number="DL1234567890",
        license_verified=True,
        vehicle_registration="MP09AB1234",
        vehicle_make="Toyota",
        vehicle_model="Innova",
        vehicle_color="White",
        insurance_expiry=datetime.utcnow() + timedelta(days=365),
        status="available"
    )
    db_session.add(driver_profile)
    db_session.commit()
    db_session.refresh(driver)
    return driver


@pytest.fixture
def driver2(db_session: Session):
    """Create second test driver."""
    driver = User(
        user_id=str(uuid.uuid4()),
        phone_number="+919876543212",
        phone_verified=True,
        name="Test Driver 2",
        email="driver2@test.com",
        user_type="driver",
        password_hash="hashed_password"  # Add password hash
    )
    db_session.add(driver)
    db_session.flush()
    
    driver_profile = DriverProfile(
        driver_id=driver.user_id,
        license_number="DL0987654321",
        license_verified=True,
        vehicle_registration="MP09CD5678",
        vehicle_make="Honda",
        vehicle_model="City",
        vehicle_color="Silver",
        insurance_expiry=datetime.utcnow() + timedelta(days=365),
        status="available"
    )
    db_session.add(driver_profile)
    db_session.commit()
    db_session.refresh(driver)
    return driver


@pytest.fixture
def ride_request(db_session: Session, rider: User):
    """Create a test ride request."""
    ride = Ride(
        ride_id=str(uuid.uuid4()),
        rider_id=rider.user_id,
        status=RideStatus.REQUESTED,
        pickup_location={
            "latitude": 22.7196,
            "longitude": 75.8577,
            "address": "Vijay Nagar, Indore"
        },
        destination={
            "latitude": 22.7532,
            "longitude": 75.8937,
            "address": "Palasia, Indore"
        },
        estimated_fare=90.0,
        fare_breakdown={
            "base": 30,
            "per_km": 12,
            "distance": 5.0,
            "surge": 1.0
        }
    )
    db_session.add(ride)
    db_session.commit()
    db_session.refresh(ride)
    return ride


def test_driver_accept_ride_success(
    db_session: Session,
    redis_client,
    rider: User,
    driver1: User,
    ride_request: Ride
):
    """Test successful driver acceptance of a ride request."""
    # Set up matching service
    matching_service = MatchingService(redis_client, db_session)
    
    # Set driver as available with location
    matching_service.set_driver_available(
        driver1.user_id,
        22.7196,  # Near pickup location
        75.8577
    )
    
    # Broadcast the ride request
    broadcast_result = matching_service.broadcast_ride_request(
        ride_id=ride_request.ride_id,
        pickup_latitude=22.7196,
        pickup_longitude=75.8577,
        destination_latitude=22.7532,
        destination_longitude=75.8937,
        estimated_fare=90.0,
        radius_km=5.0
    )
    
    assert broadcast_result["status"] == "success"
    assert driver1.user_id in [d["driver_id"] for d in broadcast_result["notified_drivers"]]
    
    # Driver accepts the ride
    match_result = matching_service.match_ride(
        ride_id=ride_request.ride_id,
        driver_id=driver1.user_id,
        rider_id=rider.user_id
    )
    
    # Verify match was successful
    assert match_result["status"] == "success"
    assert match_result["ride_id"] == ride_request.ride_id
    assert match_result["driver_id"] == driver1.user_id
    assert match_result["rider_id"] == rider.user_id
    assert "matched_at" in match_result
    assert "estimated_arrival_minutes" in match_result
    assert "driver_details" in match_result
    
    # Verify ride status updated
    db_session.refresh(ride_request)
    assert ride_request.status == RideStatus.MATCHED
    assert ride_request.driver_id == driver1.user_id
    assert ride_request.matched_at is not None
    
    # Verify driver status changed to busy
    driver_status = matching_service.get_driver_status(driver1.user_id)
    assert driver_status["status"] == "busy"
    
    # Verify broadcast was cancelled
    broadcast_details = matching_service.get_broadcast_details(ride_request.ride_id)
    assert broadcast_details["status"] == "cancelled"


def test_driver_accept_already_matched_ride(
    db: Session,
    redis_client,
    rider: User,
    driver1: User,
    driver2: User,
    ride_request: Ride
):
    """Test driver trying to accept a ride that's already matched."""
    # Set up matching service
    matching_service = MatchingService(redis_client, db_session)
    
    # Set both drivers as available
    matching_service.set_driver_available(driver1.user_id, 22.7196, 75.8577)
    matching_service.set_driver_available(driver2.user_id, 22.7200, 75.8580)
    
    # Broadcast the ride request
    matching_service.broadcast_ride_request(
        ride_id=ride_request.ride_id,
        pickup_latitude=22.7196,
        pickup_longitude=75.8577,
        destination_latitude=22.7532,
        destination_longitude=75.8937,
        estimated_fare=90.0,
        radius_km=5.0
    )
    
    # First driver accepts
    match_result1 = matching_service.match_ride(
        ride_id=ride_request.ride_id,
        driver_id=driver1.user_id,
        rider_id=rider.user_id
    )
    assert match_result1["status"] == "success"
    
    # Second driver tries to accept
    match_result2 = matching_service.match_ride(
        ride_id=ride_request.ride_id,
        driver_id=driver2.user_id,
        rider_id=rider.user_id
    )
    
    # Verify second driver gets rejection
    assert match_result2["status"] == "already_matched"
    assert "already been matched" in match_result2["message"]
    
    # Verify ride is still matched to first driver
    db_session.refresh(ride_request)
    assert ride_request.driver_id == driver1.user_id


def test_driver_reject_ride(
    db: Session,
    redis_client,
    rider: User,
    driver1: User,
    ride_request: Ride
):
    """Test driver rejecting a ride request."""
    # Set up matching service
    matching_service = MatchingService(redis_client, db_session)
    
    # Set driver as available
    matching_service.set_driver_available(driver1.user_id, 22.7196, 75.8577)
    
    # Broadcast the ride request
    broadcast_result = matching_service.broadcast_ride_request(
        ride_id=ride_request.ride_id,
        pickup_latitude=22.7196,
        pickup_longitude=75.8577,
        destination_latitude=22.7532,
        destination_longitude=75.8937,
        estimated_fare=90.0,
        radius_km=5.0
    )
    
    assert driver1.user_id in [d["driver_id"] for d in broadcast_result["notified_drivers"]]
    
    # Driver rejects the ride
    reject_result = matching_service.reject_ride(
        ride_id=ride_request.ride_id,
        driver_id=driver1.user_id
    )
    
    # Verify rejection was recorded
    assert reject_result["status"] == "success"
    assert reject_result["ride_id"] == ride_request.ride_id
    assert reject_result["driver_id"] == driver1.user_id
    assert reject_result["broadcast_still_active"] is True
    assert reject_result["rejection_count"] == 1
    
    # Verify ride is still in requested status
    db_session.refresh(ride_request)
    assert ride_request.status == RideStatus.REQUESTED
    assert ride_request.driver_id is None
    
    # Verify broadcast is still active
    broadcast_details = matching_service.get_broadcast_details(ride_request.ride_id)
    assert broadcast_details["status"] == "active"


def test_multiple_drivers_reject_then_one_accepts(
    db: Session,
    redis_client,
    rider: User,
    driver1: User,
    driver2: User,
    ride_request: Ride
):
    """Test scenario where multiple drivers reject, then one accepts."""
    # Set up matching service
    matching_service = MatchingService(redis_client, db_session)
    
    # Set both drivers as available
    matching_service.set_driver_available(driver1.user_id, 22.7196, 75.8577)
    matching_service.set_driver_available(driver2.user_id, 22.7200, 75.8580)
    
    # Broadcast the ride request
    broadcast_result = matching_service.broadcast_ride_request(
        ride_id=ride_request.ride_id,
        pickup_latitude=22.7196,
        pickup_longitude=75.8577,
        destination_latitude=22.7532,
        destination_longitude=75.8937,
        estimated_fare=90.0,
        radius_km=5.0
    )
    
    assert len(broadcast_result["notified_drivers"]) == 2
    
    # First driver rejects
    reject_result1 = matching_service.reject_ride(
        ride_id=ride_request.ride_id,
        driver_id=driver1.user_id
    )
    assert reject_result1["status"] == "success"
    assert reject_result1["remaining_drivers"] == 1
    
    # Verify ride still available
    db_session.refresh(ride_request)
    assert ride_request.status == RideStatus.REQUESTED
    
    # Second driver accepts
    match_result = matching_service.match_ride(
        ride_id=ride_request.ride_id,
        driver_id=driver2.user_id,
        rider_id=rider.user_id
    )
    
    # Verify match successful
    assert match_result["status"] == "success"
    assert match_result["driver_id"] == driver2.user_id
    
    # Verify ride matched
    db_session.refresh(ride_request)
    assert ride_request.status == RideStatus.MATCHED
    assert ride_request.driver_id == driver2.user_id


def test_driver_accept_unavailable_driver(
    db: Session,
    redis_client,
    rider: User,
    driver1: User,
    ride_request: Ride
):
    """Test driver trying to accept when they're not available."""
    # Set up matching service
    matching_service = MatchingService(redis_client, db_session)
    
    # Set driver as unavailable
    matching_service.set_driver_unavailable(driver1.user_id)
    
    # Try to match (without broadcasting first)
    match_result = matching_service.match_ride(
        ride_id=ride_request.ride_id,
        driver_id=driver1.user_id,
        rider_id=rider.user_id
    )
    
    # Verify match failed
    assert match_result["status"] == "error"
    assert "not available" in match_result["message"]
    
    # Verify ride still in requested status
    db_session.refresh(ride_request)
    assert ride_request.status == RideStatus.REQUESTED
    assert ride_request.driver_id is None


def test_driver_reject_not_notified_ride(
    db: Session,
    redis_client,
    rider: User,
    driver1: User,
    driver2: User,
    ride_request: Ride
):
    """Test driver trying to reject a ride they weren't notified about."""
    # Set up matching service
    matching_service = MatchingService(redis_client, db_session)
    
    # Set only driver1 as available and close to pickup
    matching_service.set_driver_available(driver1.user_id, 22.7196, 75.8577)
    
    # Set driver2 as available but far away (won't be notified)
    matching_service.set_driver_available(driver2.user_id, 22.8000, 75.9000)
    
    # Broadcast with small radius (only driver1 will be notified)
    broadcast_result = matching_service.broadcast_ride_request(
        ride_id=ride_request.ride_id,
        pickup_latitude=22.7196,
        pickup_longitude=75.8577,
        destination_latitude=22.7532,
        destination_longitude=75.8937,
        estimated_fare=90.0,
        radius_km=2.0  # Small radius
    )
    
    # Verify only driver1 was notified
    notified_driver_ids = [d["driver_id"] for d in broadcast_result["notified_drivers"]]
    assert driver1.user_id in notified_driver_ids
    assert driver2.user_id not in notified_driver_ids
    
    # Driver2 tries to reject
    reject_result = matching_service.reject_ride(
        ride_id=ride_request.ride_id,
        driver_id=driver2.user_id
    )
    
    # Verify rejection failed
    assert reject_result["status"] == "error"
    assert "was not notified" in reject_result["message"]


def test_match_confirmation_includes_all_details(
    db: Session,
    redis_client,
    rider: User,
    driver1: User,
    ride_request: Ride
):
    """Test that match confirmation includes all required details."""
    # Set up matching service
    matching_service = MatchingService(redis_client, db_session)
    
    # Set driver as available
    matching_service.set_driver_available(driver1.user_id, 22.7196, 75.8577)
    
    # Broadcast and match
    matching_service.broadcast_ride_request(
        ride_id=ride_request.ride_id,
        pickup_latitude=22.7196,
        pickup_longitude=75.8577,
        destination_latitude=22.7532,
        destination_longitude=75.8937,
        estimated_fare=90.0,
        radius_km=5.0
    )
    
    match_result = matching_service.match_ride(
        ride_id=ride_request.ride_id,
        driver_id=driver1.user_id,
        rider_id=rider.user_id
    )
    
    # Verify all required fields are present
    assert match_result["status"] == "success"
    assert "ride_id" in match_result
    assert "driver_id" in match_result
    assert "rider_id" in match_result
    assert "matched_at" in match_result
    assert "distance_to_pickup_km" in match_result
    assert "estimated_arrival_minutes" in match_result
    
    # Verify driver details
    assert "driver_details" in match_result
    driver_details = match_result["driver_details"]
    assert driver_details["name"] == driver1.name
    assert driver_details["phone_number"] == driver1.phone_number
    assert "rating" in driver_details
    assert "total_rides" in driver_details
    
    # Verify vehicle details
    assert "vehicle_details" in match_result
    vehicle_details = match_result["vehicle_details"]
    assert vehicle_details["registration_number"] == "MP09AB1234"
    assert vehicle_details["make"] == "Toyota"
    assert vehicle_details["model"] == "Innova"
    assert vehicle_details["color"] == "White"


def test_broadcast_cancelled_after_match(
    db: Session,
    redis_client,
    rider: User,
    driver1: User,
    driver2: User,
    ride_request: Ride
):
    """Test that broadcast is cancelled after successful match."""
    # Set up matching service
    matching_service = MatchingService(redis_client, db_session)
    
    # Set both drivers as available
    matching_service.set_driver_available(driver1.user_id, 22.7196, 75.8577)
    matching_service.set_driver_available(driver2.user_id, 22.7200, 75.8580)
    
    # Broadcast the ride request
    broadcast_result = matching_service.broadcast_ride_request(
        ride_id=ride_request.ride_id,
        pickup_latitude=22.7196,
        pickup_longitude=75.8577,
        destination_latitude=22.7532,
        destination_longitude=75.8937,
        estimated_fare=90.0,
        radius_km=5.0
    )
    
    # Verify broadcast is active
    broadcast_details = matching_service.get_broadcast_details(ride_request.ride_id)
    assert broadcast_details["status"] == "active"
    assert len(broadcast_details["notified_drivers"]) == 2
    
    # Driver1 accepts
    match_result = matching_service.match_ride(
        ride_id=ride_request.ride_id,
        driver_id=driver1.user_id,
        rider_id=rider.user_id
    )
    assert match_result["status"] == "success"
    
    # Verify broadcast is now cancelled
    broadcast_details = matching_service.get_broadcast_details(ride_request.ride_id)
    assert broadcast_details["status"] == "cancelled"
    assert "cancelled_at" in broadcast_details
