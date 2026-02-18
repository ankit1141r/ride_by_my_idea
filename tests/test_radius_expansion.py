"""
Tests for search radius expansion functionality.
Tests Requirement 3.5.
"""
import pytest
from app.services.matching_service import MatchingService
from app.models.user import User, DriverProfile
from app.models.ride import Ride, RideStatus
from datetime import datetime, timedelta


def test_expand_search_radius_success(db_session, redis_client):
    """Test successful search radius expansion."""
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
    
    # Create drivers at different distances
    driver1 = User(
        user_id="driver1",
        phone_number="+919876543211",
        name="Close Driver",
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
        name="Far Driver",
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
    
    # Set drivers at different distances
    # Driver1 at ~1km (within initial 5km radius)
    matching_service.set_driver_available("driver1", 22.7286, 75.8577)
    # Driver2 at ~6km (outside initial 5km, but within 7km)
    matching_service.set_driver_available("driver2", 22.7730, 75.8577)
    
    # Initial broadcast with 5km radius
    initial_broadcast = matching_service.broadcast_ride_request(
        ride_id="ride123",
        pickup_latitude=22.7196,
        pickup_longitude=75.8577,
        destination_latitude=22.7500,
        destination_longitude=75.8700,
        estimated_fare=150.0,
        radius_km=5.0
    )
    
    # Only driver1 should be notified initially
    assert initial_broadcast["drivers_notified"] == 1
    assert initial_broadcast["notified_drivers"][0]["driver_id"] == "driver1"
    
    # Expand search radius by 2km (5km -> 7km)
    expansion_result = matching_service.expand_search_radius(
        ride_id="ride123",
        current_radius_km=5.0,
        expansion_km=2.0
    )
    
    # Verify expansion result
    assert expansion_result["status"] == "success"
    assert expansion_result["ride_id"] == "ride123"
    assert expansion_result["previous_radius_km"] == 5.0
    assert expansion_result["new_radius_km"] == 7.0
    assert expansion_result["expansion_km"] == 2.0
    assert expansion_result["broadcast_count"] == 2
    assert expansion_result["newly_notified_drivers"] == 1
    assert expansion_result["total_notified_drivers"] == 2
    assert "driver2" in expansion_result["newly_included_driver_ids"]
    
    # Verify broadcast details updated
    broadcast_details = matching_service.get_broadcast_details("ride123")
    assert broadcast_details["radius_km"] == 7.0
    assert broadcast_details["broadcast_count"] == 2
    assert "driver1" in broadcast_details["notified_drivers"]
    assert "driver2" in broadcast_details["notified_drivers"]
    assert "last_expansion_at" in broadcast_details


def test_expand_search_radius_no_new_drivers(db_session, redis_client):
    """Test radius expansion when no new drivers are in expanded area."""
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
        name="Close Driver",
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
    
    # Set driver within initial radius
    matching_service.set_driver_available("driver1", 22.7286, 75.8577)
    
    # Initial broadcast
    matching_service.broadcast_ride_request(
        ride_id="ride123",
        pickup_latitude=22.7196,
        pickup_longitude=75.8577,
        destination_latitude=22.7500,
        destination_longitude=75.8700,
        estimated_fare=150.0,
        radius_km=5.0
    )
    
    # Expand radius (no new drivers in expanded area)
    expansion_result = matching_service.expand_search_radius(
        ride_id="ride123",
        current_radius_km=5.0,
        expansion_km=2.0
    )
    
    # Should succeed but with no newly notified drivers
    assert expansion_result["status"] == "success"
    assert expansion_result["newly_notified_drivers"] == 0
    assert expansion_result["total_notified_drivers"] == 1


def test_expand_search_radius_ride_not_found(db_session, redis_client):
    """Test radius expansion with non-existent ride."""
    matching_service = MatchingService(redis_client, db_session)
    
    result = matching_service.expand_search_radius(
        ride_id="nonexistent",
        current_radius_km=5.0,
        expansion_km=2.0
    )
    
    assert result["status"] == "error"
    assert "not found" in result["message"].lower()


def test_expand_search_radius_ride_already_matched(db_session, redis_client):
    """Test that radius cannot be expanded for matched rides."""
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
    
    # Try to expand radius for matched ride
    result = matching_service.expand_search_radius(
        ride_id="ride123",
        current_radius_km=5.0,
        expansion_km=2.0
    )
    
    assert result["status"] == "error"
    assert "no longer in requested status" in result["message"].lower()


def test_expand_search_radius_multiple_times(db_session, redis_client):
    """Test multiple radius expansions."""
    # Create rider and drivers at various distances
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
        name="Close Driver",
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
        name="Medium Driver",
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
        name="Far Driver",
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
    
    # Set drivers at different distances
    matching_service.set_driver_available("driver1", 22.7286, 75.8577)  # ~1km
    matching_service.set_driver_available("driver2", 22.7730, 75.8577)  # ~6km
    matching_service.set_driver_available("driver3", 22.7900, 75.8577)  # ~8km
    
    # Initial broadcast with 5km radius
    initial_broadcast = matching_service.broadcast_ride_request(
        ride_id="ride123",
        pickup_latitude=22.7196,
        pickup_longitude=75.8577,
        destination_latitude=22.7500,
        destination_longitude=75.8700,
        estimated_fare=150.0,
        radius_km=5.0
    )
    assert initial_broadcast["drivers_notified"] == 1
    
    # First expansion: 5km -> 7km (should include driver2)
    expansion1 = matching_service.expand_search_radius(
        ride_id="ride123",
        current_radius_km=5.0,
        expansion_km=2.0
    )
    assert expansion1["status"] == "success"
    assert expansion1["new_radius_km"] == 7.0
    assert expansion1["broadcast_count"] == 2
    assert expansion1["newly_notified_drivers"] == 1
    assert expansion1["total_notified_drivers"] == 2
    
    # Second expansion: 7km -> 9km (should include driver3)
    expansion2 = matching_service.expand_search_radius(
        ride_id="ride123",
        current_radius_km=7.0,
        expansion_km=2.0
    )
    assert expansion2["status"] == "success"
    assert expansion2["new_radius_km"] == 9.0
    assert expansion2["broadcast_count"] == 3
    assert expansion2["newly_notified_drivers"] == 1
    assert expansion2["total_notified_drivers"] == 3
    
    # Verify all drivers notified
    broadcast_details = matching_service.get_broadcast_details("ride123")
    assert len(broadcast_details["notified_drivers"]) == 3
    assert "driver1" in broadcast_details["notified_drivers"]
    assert "driver2" in broadcast_details["notified_drivers"]
    assert "driver3" in broadcast_details["notified_drivers"]
