"""
Tests for driver rejection handling functionality.
Tests Requirement 3.4.
"""
import pytest
from app.services.matching_service import MatchingService
from app.models.user import User, DriverProfile
from app.models.ride import Ride, RideStatus
from datetime import datetime, timedelta


def test_reject_ride_success(db_session, redis_client):
    """Test successful ride rejection by driver."""
    # Create rider and driver
    rider = User(
        user_id="rider1",
        phone_number="+919876543210",
        name="Test Rider",
        email="rider@test.com",
        user_type="rider",
        phone_verified=True,
        password_hash="hashed_password"
    )
    
    driver = User(
        user_id="driver1",
        phone_number="+919876543211",
        name="Test Driver",
        email="driver1@test.com",
        user_type="driver",
        phone_verified=True,
        password_hash="hashed_password"
    )
    driver.driver_profile = DriverProfile(
        driver_id="driver1",
        license_number="DL1234567890",
        vehicle_registration="MP09AB1234",
        vehicle_make="Maruti",
        vehicle_model="Swift",
        vehicle_color="White",
        insurance_expiry=datetime.utcnow() + timedelta(days=365),
        status="available"
    )
    
    # Create ride request
    ride = Ride(
        ride_id="ride123",
        rider_id="rider1",
        status=RideStatus.REQUESTED,
        pickup_location={
            "latitude": 22.7196,
            "longitude": 75.8577,
            "address": "Vijay Nagar, Indore"
        },
        destination={
            "latitude": 22.7500,
            "longitude": 75.8700,
            "address": "Palasia, Indore"
        },
        estimated_fare=150.0,
        fare_breakdown={
            "base_fare": 30.0,
            "distance_charge": 120.0,
            "surge_multiplier": 1.0
        }
    )
    
    db_session.add_all([rider, driver, ride])
    db_session.commit()
    
    matching_service = MatchingService(redis_client, db_session)
    
    # Set driver as available
    matching_service.set_driver_available("driver1", 22.7286, 75.8577)
    
    # Broadcast ride request
    matching_service.broadcast_ride_request(
        ride_id="ride123",
        pickup_latitude=22.7196,
        pickup_longitude=75.8577,
        destination_latitude=22.7500,
        destination_longitude=75.8700,
        estimated_fare=150.0,
        radius_km=5.0
    )
    
    # Driver rejects the ride
    result = matching_service.reject_ride(
        ride_id="ride123",
        driver_id="driver1"
    )
    
    # Verify rejection result
    assert result["status"] == "success"
    assert result["ride_id"] == "ride123"
    assert result["driver_id"] == "driver1"
    assert "rejected_at" in result
    assert result["rejection_count"] == 1
    assert result["broadcast_still_active"] is True
    
    # Verify ride is still in requested status
    db_session.refresh(ride)
    assert ride.status == RideStatus.REQUESTED
    
    # Verify broadcast is still active
    broadcast_details = matching_service.get_broadcast_details("ride123")
    assert broadcast_details is not None
    assert broadcast_details["status"] == "active"


def test_reject_ride_multiple_drivers(db_session, redis_client):
    """Test multiple drivers rejecting the same ride."""
    # Create rider and multiple drivers
    rider = User(
        user_id="rider1",
        phone_number="+919876543210",
        name="Test Rider",
        email="rider@test.com",
        user_type="rider",
        phone_verified=True,
        password_hash="hashed_password"
    )
    
    driver1 = User(
        user_id="driver1",
        phone_number="+919876543211",
        name="Driver One",
        email="driver1@test.com",
        user_type="driver",
        phone_verified=True,
        password_hash="hashed_password"
    )
    driver1.driver_profile = DriverProfile(
        driver_id="driver1",
        license_number="DL1234567890",
        vehicle_registration="MP09AB1234",
        vehicle_make="Maruti",
        vehicle_model="Swift",
        vehicle_color="White",
        insurance_expiry=datetime.utcnow() + timedelta(days=365),
        status="available"
    )
    
    driver2 = User(
        user_id="driver2",
        phone_number="+919876543212",
        name="Driver Two",
        email="driver2@test.com",
        user_type="driver",
        phone_verified=True,
        password_hash="hashed_password"
    )
    driver2.driver_profile = DriverProfile(
        driver_id="driver2",
        license_number="DL2234567890",
        vehicle_registration="MP09AB5678",
        vehicle_make="Hyundai",
        vehicle_model="i20",
        vehicle_color="Red",
        insurance_expiry=datetime.utcnow() + timedelta(days=365),
        status="available"
    )
    
    driver3 = User(
        user_id="driver3",
        phone_number="+919876543213",
        name="Driver Three",
        email="driver3@test.com",
        user_type="driver",
        phone_verified=True,
        password_hash="hashed_password"
    )
    driver3.driver_profile = DriverProfile(
        driver_id="driver3",
        license_number="DL3234567890",
        vehicle_registration="MP09AB9012",
        vehicle_make="Honda",
        vehicle_model="City",
        vehicle_color="Blue",
        insurance_expiry=datetime.utcnow() + timedelta(days=365),
        status="available"
    )
    
    # Create ride request
    ride = Ride(
        ride_id="ride123",
        rider_id="rider1",
        status=RideStatus.REQUESTED,
        pickup_location={
            "latitude": 22.7196,
            "longitude": 75.8577,
            "address": "Vijay Nagar, Indore"
        },
        destination={
            "latitude": 22.7500,
            "longitude": 75.8700,
            "address": "Palasia, Indore"
        },
        estimated_fare=150.0,
        fare_breakdown={
            "base_fare": 30.0,
            "distance_charge": 120.0,
            "surge_multiplier": 1.0
        }
    )
    
    db_session.add_all([rider, driver1, driver2, driver3, ride])
    db_session.commit()
    
    matching_service = MatchingService(redis_client, db_session)
    
    # Set all drivers as available
    matching_service.set_driver_available("driver1", 22.7286, 75.8577)
    matching_service.set_driver_available("driver2", 22.7300, 75.8577)
    matching_service.set_driver_available("driver3", 22.7320, 75.8577)
    
    # Broadcast ride request
    broadcast_result = matching_service.broadcast_ride_request(
        ride_id="ride123",
        pickup_latitude=22.7196,
        pickup_longitude=75.8577,
        destination_latitude=22.7500,
        destination_longitude=75.8700,
        estimated_fare=150.0,
        radius_km=5.0
    )
    
    assert broadcast_result["drivers_notified"] == 3
    
    # First driver rejects
    result1 = matching_service.reject_ride("ride123", "driver1")
    assert result1["status"] == "success"
    assert result1["rejection_count"] == 1
    assert result1["remaining_drivers"] == 2
    
    # Second driver rejects
    result2 = matching_service.reject_ride("ride123", "driver2")
    assert result2["status"] == "success"
    assert result2["rejection_count"] == 2
    assert result2["remaining_drivers"] == 1
    
    # Ride should still be active for driver3
    assert result2["broadcast_still_active"] is True
    
    # Verify ride is still in requested status
    db_session.refresh(ride)
    assert ride.status == RideStatus.REQUESTED


def test_reject_ride_not_notified(db_session, redis_client):
    """Test that driver who wasn't notified cannot reject."""
    # Create rider and drivers
    rider = User(
        user_id="rider1",
        phone_number="+919876543210",
        name="Test Rider",
        email="rider@test.com",
        user_type="rider",
        phone_verified=True,
        password_hash="hashed_password"
    )
    
    driver1 = User(
        user_id="driver1",
        phone_number="+919876543211",
        name="Notified Driver",
        email="driver1@test.com",
        user_type="driver",
        phone_verified=True,
        password_hash="hashed_password"
    )
    driver1.driver_profile = DriverProfile(
        driver_id="driver1",
        license_number="DL1234567890",
        vehicle_registration="MP09AB1234",
        vehicle_make="Maruti",
        vehicle_model="Swift",
        vehicle_color="White",
        insurance_expiry=datetime.utcnow() + timedelta(days=365),
        status="available"
    )
    
    driver2 = User(
        user_id="driver2",
        phone_number="+919876543212",
        name="Not Notified Driver",
        email="driver2@test.com",
        user_type="driver",
        phone_verified=True,
        password_hash="hashed_password"
    )
    driver2.driver_profile = DriverProfile(
        driver_id="driver2",
        license_number="DL2234567890",
        vehicle_registration="MP09AB5678",
        vehicle_make="Hyundai",
        vehicle_model="i20",
        vehicle_color="Red",
        insurance_expiry=datetime.utcnow() + timedelta(days=365),
        status="available"
    )
    
    # Create ride request
    ride = Ride(
        ride_id="ride123",
        rider_id="rider1",
        status=RideStatus.REQUESTED,
        pickup_location={
            "latitude": 22.7196,
            "longitude": 75.8577,
            "address": "Vijay Nagar, Indore"
        },
        destination={
            "latitude": 22.7500,
            "longitude": 75.8700,
            "address": "Palasia, Indore"
        },
        estimated_fare=150.0,
        fare_breakdown={
            "base_fare": 30.0,
            "distance_charge": 120.0,
            "surge_multiplier": 1.0
        }
    )
    
    db_session.add_all([rider, driver1, driver2, ride])
    db_session.commit()
    
    matching_service = MatchingService(redis_client, db_session)
    
    # Only driver1 is within radius
    matching_service.set_driver_available("driver1", 22.7286, 75.8577)
    # Driver2 is far away (not notified)
    matching_service.set_driver_available("driver2", 22.8000, 75.8577)
    
    # Broadcast ride request with 5km radius
    matching_service.broadcast_ride_request(
        ride_id="ride123",
        pickup_latitude=22.7196,
        pickup_longitude=75.8577,
        destination_latitude=22.7500,
        destination_longitude=75.8700,
        estimated_fare=150.0,
        radius_km=5.0
    )
    
    # Driver2 tries to reject (but wasn't notified)
    result = matching_service.reject_ride("ride123", "driver2")
    
    assert result["status"] == "error"
    assert "not notified" in result["message"].lower()


def test_reject_ride_already_matched(db_session, redis_client):
    """Test that ride cannot be rejected after it's matched."""
    # Create rider and driver
    rider = User(
        user_id="rider1",
        phone_number="+919876543210",
        name="Test Rider",
        email="rider@test.com",
        user_type="rider",
        phone_verified=True,
        password_hash="hashed_password"
    )
    
    driver = User(
        user_id="driver1",
        phone_number="+919876543211",
        name="Test Driver",
        email="driver1@test.com",
        user_type="driver",
        phone_verified=True,
        password_hash="hashed_password"
    )
    driver.driver_profile = DriverProfile(
        driver_id="driver1",
        license_number="DL1234567890",
        vehicle_registration="MP09AB1234",
        vehicle_make="Maruti",
        vehicle_model="Swift",
        vehicle_color="White",
        insurance_expiry=datetime.utcnow() + timedelta(days=365),
        status="available"
    )
    
    # Create ride that's already matched
    ride = Ride(
        ride_id="ride123",
        rider_id="rider1",
        driver_id="driver1",
        status=RideStatus.MATCHED,
        pickup_location={
            "latitude": 22.7196,
            "longitude": 75.8577,
            "address": "Vijay Nagar, Indore"
        },
        destination={
            "latitude": 22.7500,
            "longitude": 75.8700,
            "address": "Palasia, Indore"
        },
        estimated_fare=150.0,
        fare_breakdown={
            "base_fare": 30.0,
            "distance_charge": 120.0,
            "surge_multiplier": 1.0
        },
        matched_at=datetime.utcnow()
    )
    
    db_session.add_all([rider, driver, ride])
    db_session.commit()
    
    matching_service = MatchingService(redis_client, db_session)
    
    # Try to reject matched ride
    result = matching_service.reject_ride("ride123", "driver1")
    
    assert result["status"] == "error"
    assert "no longer available" in result["message"].lower()


def test_reject_ride_nonexistent(db_session, redis_client):
    """Test rejection of non-existent ride."""
    matching_service = MatchingService(redis_client, db_session)
    
    result = matching_service.reject_ride("nonexistent", "driver1")
    
    assert result["status"] == "error"
    assert "not found" in result["message"].lower()


def test_reject_ride_removes_notification(db_session, redis_client):
    """Test that rejection removes notification from driver's queue."""
    # Create rider and driver
    rider = User(
        user_id="rider1",
        phone_number="+919876543210",
        name="Test Rider",
        email="rider@test.com",
        user_type="rider",
        phone_verified=True,
        password_hash="hashed_password"
    )
    
    driver = User(
        user_id="driver1",
        phone_number="+919876543211",
        name="Test Driver",
        email="driver1@test.com",
        user_type="driver",
        phone_verified=True,
        password_hash="hashed_password"
    )
    driver.driver_profile = DriverProfile(
        driver_id="driver1",
        license_number="DL1234567890",
        vehicle_registration="MP09AB1234",
        vehicle_make="Maruti",
        vehicle_model="Swift",
        vehicle_color="White",
        insurance_expiry=datetime.utcnow() + timedelta(days=365),
        status="available"
    )
    
    # Create ride request
    ride = Ride(
        ride_id="ride123",
        rider_id="rider1",
        status=RideStatus.REQUESTED,
        pickup_location={
            "latitude": 22.7196,
            "longitude": 75.8577,
            "address": "Vijay Nagar, Indore"
        },
        destination={
            "latitude": 22.7500,
            "longitude": 75.8700,
            "address": "Palasia, Indore"
        },
        estimated_fare=150.0,
        fare_breakdown={
            "base_fare": 30.0,
            "distance_charge": 120.0,
            "surge_multiplier": 1.0
        }
    )
    
    db_session.add_all([rider, driver, ride])
    db_session.commit()
    
    matching_service = MatchingService(redis_client, db_session)
    
    # Set driver as available
    matching_service.set_driver_available("driver1", 22.7286, 75.8577)
    
    # Broadcast ride request
    matching_service.broadcast_ride_request(
        ride_id="ride123",
        pickup_latitude=22.7196,
        pickup_longitude=75.8577,
        destination_latitude=22.7500,
        destination_longitude=75.8700,
        estimated_fare=150.0,
        radius_km=5.0
    )
    
    # Verify notification exists
    driver_notification_key = f"driver:notifications:driver1"
    notifications_before = redis_client.zrange(driver_notification_key, 0, -1)
    assert len(notifications_before) == 1
    
    # Driver rejects the ride
    matching_service.reject_ride("ride123", "driver1")
    
    # Verify notification is removed
    notifications_after = redis_client.zrange(driver_notification_key, 0, -1)
    assert len(notifications_after) == 0
