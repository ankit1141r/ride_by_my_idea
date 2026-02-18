"""
Tests for ride matching functionality.
Tests Requirements 3.3, 3.6, 4.1.
"""
import pytest
from app.services.matching_service import MatchingService
from app.models.user import User, DriverProfile
from app.models.ride import Ride, RideStatus
from datetime import datetime, timedelta
import time


def test_match_ride_success(db_session, redis_client):
    """Test successful ride matching."""
    # Create rider
    rider = User(
        user_id="rider1",
        phone_number="+919876543210",
        name="Test Rider",
        email="rider@test.com",
        user_type="rider",
        phone_verified=True,
        password_hash="hashed_password"
    )
    
    # Create driver
    driver = User(
        user_id="driver1",
        phone_number="+919876543211",
        name="Test Driver",
        email="driver@test.com",
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
    
    # Set driver as available with location
    matching_service.set_driver_available("driver1", 22.7286, 75.8577)
    
    # Match the ride
    result = matching_service.match_ride(
        ride_id="ride123",
        driver_id="driver1",
        rider_id="rider1"
    )
    
    # Verify match result
    assert result["status"] == "success"
    assert result["ride_id"] == "ride123"
    assert result["driver_id"] == "driver1"
    assert result["rider_id"] == "rider1"
    assert "matched_at" in result
    assert "distance_to_pickup_km" in result
    assert "estimated_arrival_minutes" in result
    assert "driver_details" in result
    assert "vehicle_details" in result
    
    # Verify ride status updated
    db_session.refresh(ride)
    assert ride.status == RideStatus.MATCHED
    assert ride.driver_id == "driver1"
    assert ride.matched_at is not None
    
    # Verify driver status changed to busy
    assert not matching_service.is_driver_available("driver1")
    driver_status = matching_service.get_driver_status("driver1")
    assert driver_status["status"] == "busy"


def test_match_ride_already_matched(db_session, redis_client):
    """Test that a ride cannot be matched twice."""
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
    
    # Set both drivers as available
    matching_service.set_driver_available("driver1", 22.7286, 75.8577)
    matching_service.set_driver_available("driver2", 22.7300, 75.8577)
    
    # Match with first driver
    result1 = matching_service.match_ride(
        ride_id="ride123",
        driver_id="driver1",
        rider_id="rider1"
    )
    assert result1["status"] == "success"
    
    # Try to match with second driver
    result2 = matching_service.match_ride(
        ride_id="ride123",
        driver_id="driver2",
        rider_id="rider1"
    )
    
    # Should fail because ride is already matched
    assert result2["status"] == "error"
    assert "no longer available" in result2["message"].lower()


def test_match_ride_driver_not_available(db_session, redis_client):
    """Test that unavailable driver cannot be matched."""
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
        email="driver@test.com",
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
        status="unavailable"
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
    
    # Try to match without setting driver as available
    result = matching_service.match_ride(
        ride_id="ride123",
        driver_id="driver1",
        rider_id="rider1"
    )
    
    # Should fail
    assert result["status"] == "error"
    assert "not available" in result["message"].lower()


def test_match_ride_nonexistent_ride(db_session, redis_client):
    """Test matching with non-existent ride ID."""
    # Create driver
    driver = User(
        user_id="driver1",
        phone_number="+919876543211",
        name="Test Driver",
        email="driver@test.com",
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
    
    db_session.add(driver)
    db_session.commit()
    
    matching_service = MatchingService(redis_client, db_session)
    matching_service.set_driver_available("driver1", 22.7286, 75.8577)
    
    # Try to match non-existent ride
    result = matching_service.match_ride(
        ride_id="nonexistent",
        driver_id="driver1",
        rider_id="rider1"
    )
    
    assert result["status"] == "error"
    assert "not found" in result["message"].lower()


def test_match_ride_updates_driver_to_busy(db_session, redis_client):
    """Test that matching a ride updates driver status to busy."""
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
        email="driver@test.com",
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
    assert matching_service.is_driver_available("driver1")
    
    # Match the ride
    result = matching_service.match_ride(
        ride_id="ride123",
        driver_id="driver1",
        rider_id="rider1"
    )
    
    assert result["status"] == "success"
    
    # Verify driver is no longer available (now busy)
    assert not matching_service.is_driver_available("driver1")
    
    # Verify driver status is busy
    driver_status = matching_service.get_driver_status("driver1")
    assert driver_status["status"] == "busy"
    
    # Verify in database
    db_session.refresh(driver)
    assert driver.driver_profile.status == "busy"
