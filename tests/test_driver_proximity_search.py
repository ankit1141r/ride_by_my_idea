"""
Tests for driver proximity search functionality.
Tests Requirements 3.1 and 4.3.
"""
import pytest
from app.services.matching_service import MatchingService
from app.models.user import User, DriverProfile
from datetime import datetime, timedelta


def test_get_available_drivers_within_radius(db_session, redis_client):
    """Test that only drivers within specified radius are returned."""
    # Create test drivers at different distances
    # Pickup location: 22.7196, 75.8577 (Indore center)
    pickup_lat, pickup_lon = 22.7196, 75.8577
    
    # Driver 1: ~2km away (should be included in 5km radius)
    driver1 = User(
        user_id="driver1",
        phone_number="+919876543210",
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
    
    # Driver 2: ~4km away (should be included in 5km radius)
    driver2 = User(
        user_id="driver2",
        phone_number="+919876543211",
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
    
    # Driver 3: ~7km away (should NOT be included in 5km radius)
    driver3 = User(
        user_id="driver3",
        phone_number="+919876543212",
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
    
    db_session.add_all([driver1, driver2, driver3])
    db_session.commit()
    
    # Set drivers as available with their locations
    matching_service = MatchingService(redis_client, db_session)
    
    # Driver 1 at ~2km distance
    matching_service.set_driver_available("driver1", 22.7380, 75.8577)
    
    # Driver 2 at ~4km distance
    matching_service.set_driver_available("driver2", 22.7560, 75.8577)
    
    # Driver 3 at ~7km distance
    matching_service.set_driver_available("driver3", 22.7830, 75.8577)
    
    # Search for drivers within 5km
    available_drivers = matching_service.get_available_drivers(
        pickup_lat, pickup_lon, radius_km=5.0
    )
    
    # Should only return driver1 and driver2
    assert len(available_drivers) == 2
    driver_ids = [d["driver_id"] for d in available_drivers]
    assert "driver1" in driver_ids
    assert "driver2" in driver_ids
    assert "driver3" not in driver_ids


def test_drivers_sorted_by_distance(db_session, redis_client):
    """Test that drivers are sorted by distance (closest first) - Requirement 4.3."""
    pickup_lat, pickup_lon = 22.7196, 75.8577
    
    # Create three drivers at different distances
    driver1 = User(
        user_id="driver1",
        phone_number="+919876543210",
        name="Driver One",
        email="driver1@test.com",
        user_type="driver",
        phone_verified=True,
        password_hash="hashed_password",
        average_rating=4.5,
        total_rides=100
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
        phone_number="+919876543211",
        name="Driver Two",
        email="driver2@test.com",
        user_type="driver",
        phone_verified=True,
        password_hash="hashed_password",
        average_rating=4.8,
        total_rides=150
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
        phone_number="+919876543212",
        name="Driver Three",
        email="driver3@test.com",
        user_type="driver",
        phone_verified=True,
        password_hash="hashed_password",
        average_rating=4.2,
        total_rides=80
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
    
    db_session.add_all([driver1, driver2, driver3])
    db_session.commit()
    
    matching_service = MatchingService(redis_client, db_session)
    
    # Set drivers at different distances (intentionally not in order)
    # Driver 1 at ~4km
    matching_service.set_driver_available("driver1", 22.7560, 75.8577)
    
    # Driver 2 at ~1km (closest)
    matching_service.set_driver_available("driver2", 22.7286, 75.8577)
    
    # Driver 3 at ~2.5km
    matching_service.set_driver_available("driver3", 22.7420, 75.8577)
    
    # Get available drivers
    available_drivers = matching_service.get_available_drivers(
        pickup_lat, pickup_lon, radius_km=5.0
    )
    
    # Should return all 3 drivers
    assert len(available_drivers) == 3
    
    # Verify they are sorted by distance (closest first)
    assert available_drivers[0]["driver_id"] == "driver2"  # ~1km
    assert available_drivers[1]["driver_id"] == "driver3"  # ~2.5km
    assert available_drivers[2]["driver_id"] == "driver1"  # ~4km
    
    # Verify distances are increasing
    assert available_drivers[0]["distance_km"] < available_drivers[1]["distance_km"]
    assert available_drivers[1]["distance_km"] < available_drivers[2]["distance_km"]


def test_only_available_drivers_returned(db_session, redis_client):
    """Test that only drivers with 'available' status are returned."""
    pickup_lat, pickup_lon = 22.7196, 75.8577
    
    # Create drivers with different statuses
    driver1 = User(
        user_id="driver1",
        phone_number="+919876543210",
        name="Available Driver",
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
        phone_number="+919876543211",
        name="Busy Driver",
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
        status="busy"
    )
    
    driver3 = User(
        user_id="driver3",
        phone_number="+919876543212",
        name="Unavailable Driver",
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
        status="unavailable"
    )
    
    db_session.add_all([driver1, driver2, driver3])
    db_session.commit()
    
    matching_service = MatchingService(redis_client, db_session)
    
    # Only set driver1 as available
    matching_service.set_driver_available("driver1", 22.7286, 75.8577)
    
    # Set driver2 as busy
    matching_service.set_driver_busy("driver2")
    
    # Driver3 is not set to any status (implicitly unavailable)
    
    # Get available drivers
    available_drivers = matching_service.get_available_drivers(
        pickup_lat, pickup_lon, radius_km=5.0
    )
    
    # Should only return driver1
    assert len(available_drivers) == 1
    assert available_drivers[0]["driver_id"] == "driver1"


def test_driver_details_included_in_response(db_session, redis_client):
    """Test that driver details include all required information."""
    pickup_lat, pickup_lon = 22.7196, 75.8577
    
    driver = User(
        user_id="driver1",
        phone_number="+919876543210",
        name="Test Driver",
        email="driver@test.com",
        user_type="driver",
        phone_verified=True,
        password_hash="hashed_password",
        average_rating=4.7,
        total_rides=250
    )
    driver.driver_profile = DriverProfile(
        driver_id="driver1",
        license_number="DL1234567890",
        vehicle_registration="MP09AB1234",
        vehicle_make="Maruti",
        vehicle_model="Swift Dzire",
        vehicle_color="Silver",
        insurance_expiry=datetime.utcnow() + timedelta(days=365),
        status="available"
    )
    
    db_session.add(driver)
    db_session.commit()
    
    matching_service = MatchingService(redis_client, db_session)
    matching_service.set_driver_available("driver1", 22.7286, 75.8577)
    
    # Get available drivers
    available_drivers = matching_service.get_available_drivers(
        pickup_lat, pickup_lon, radius_km=5.0
    )
    
    assert len(available_drivers) == 1
    driver_data = available_drivers[0]
    
    # Verify all required fields are present
    assert driver_data["driver_id"] == "driver1"
    assert driver_data["name"] == "Test Driver"
    assert driver_data["phone_number"] == "+919876543210"
    assert "latitude" in driver_data
    assert "longitude" in driver_data
    assert "distance_km" in driver_data
    assert driver_data["rating"] == 4.7
    assert driver_data["total_rides"] == 250
    
    # Verify vehicle details
    assert driver_data["vehicle"] is not None
    assert driver_data["vehicle"]["registration_number"] == "MP09AB1234"
    assert driver_data["vehicle"]["make"] == "Maruti"
    assert driver_data["vehicle"]["model"] == "Swift Dzire"
    assert driver_data["vehicle"]["color"] == "Silver"


def test_empty_result_when_no_drivers_in_radius(db_session, redis_client):
    """Test that empty list is returned when no drivers are within radius."""
    pickup_lat, pickup_lon = 22.7196, 75.8577
    
    # Create a driver far away
    driver = User(
        user_id="driver1",
        phone_number="+919876543210",
        name="Far Driver",
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
    
    # Set driver at ~10km distance
    matching_service.set_driver_available("driver1", 22.8096, 75.8577)
    
    # Search with 5km radius
    available_drivers = matching_service.get_available_drivers(
        pickup_lat, pickup_lon, radius_km=5.0
    )
    
    # Should return empty list
    assert len(available_drivers) == 0


def test_custom_radius_parameter(db_session, redis_client):
    """Test that custom radius parameter works correctly."""
    pickup_lat, pickup_lon = 22.7196, 75.8577
    
    driver = User(
        user_id="driver1",
        phone_number="+919876543210",
        name="Driver",
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
    
    # Set driver at ~7km distance
    matching_service.set_driver_available("driver1", 22.7830, 75.8577)
    
    # Search with 5km radius - should not find driver
    available_drivers_5km = matching_service.get_available_drivers(
        pickup_lat, pickup_lon, radius_km=5.0
    )
    assert len(available_drivers_5km) == 0
    
    # Search with 10km radius - should find driver
    available_drivers_10km = matching_service.get_available_drivers(
        pickup_lat, pickup_lon, radius_km=10.0
    )
    assert len(available_drivers_10km) == 1
    assert available_drivers_10km[0]["driver_id"] == "driver1"
