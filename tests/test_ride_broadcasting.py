"""
Tests for ride broadcasting functionality.
Tests Requirements 2.3 and 3.1.
"""
import pytest
import json
from app.services.matching_service import MatchingService
from app.services.location_service import calculate_distance
from app.models.user import User, DriverProfile
from datetime import datetime, timedelta


def test_broadcast_ride_request_to_drivers_in_radius(db_session, redis_client):
    """Test that ride request is broadcast to all available drivers within radius."""
    # Create test drivers
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
    
    db_session.add_all([driver1, driver2])
    db_session.commit()
    
    matching_service = MatchingService(redis_client, db_session)
    
    # Set drivers as available
    matching_service.set_driver_available("driver1", 22.7286, 75.8577)  # ~1km from pickup
    matching_service.set_driver_available("driver2", 22.7420, 75.8577)  # ~2.5km from pickup
    
    # Broadcast ride request
    pickup_lat, pickup_lon = 22.7196, 75.8577
    dest_lat, dest_lon = 22.7500, 75.8700
    
    result = matching_service.broadcast_ride_request(
        ride_id="ride123",
        pickup_latitude=pickup_lat,
        pickup_longitude=pickup_lon,
        destination_latitude=dest_lat,
        destination_longitude=dest_lon,
        estimated_fare=150.0,
        radius_km=5.0
    )
    
    # Verify broadcast result
    assert result["status"] == "success"
    assert result["ride_id"] == "ride123"
    assert result["broadcast_radius_km"] == 5.0
    assert result["drivers_notified"] == 2
    
    # Verify both drivers were notified
    notified_driver_ids = [d["driver_id"] for d in result["notified_drivers"]]
    assert "driver1" in notified_driver_ids
    assert "driver2" in notified_driver_ids


def test_broadcast_stores_details_in_redis(db_session, redis_client):
    """Test that broadcast details are stored in Redis."""
    driver = User(
        user_id="driver1",
        phone_number="+919876543210",
        name="Driver One",
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
    
    db_session.add(driver)
    db_session.commit()
    
    matching_service = MatchingService(redis_client, db_session)
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
    
    # Retrieve broadcast details
    broadcast_details = matching_service.get_broadcast_details("ride123")
    
    assert broadcast_details is not None
    assert broadcast_details["ride_id"] == "ride123"
    assert broadcast_details["pickup_latitude"] == 22.7196
    assert broadcast_details["pickup_longitude"] == 75.8577
    assert broadcast_details["destination_latitude"] == 22.7500
    assert broadcast_details["destination_longitude"] == 75.8700
    assert broadcast_details["estimated_fare"] == 150.0
    assert broadcast_details["radius_km"] == 5.0
    assert broadcast_details["status"] == "active"
    assert "driver1" in broadcast_details["notified_drivers"]


def test_broadcast_respects_radius(db_session, redis_client):
    """Test that only drivers within radius are notified."""
    # Create drivers at different distances
    driver1 = User(
        user_id="driver1",
        phone_number="+919876543210",
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
        phone_number="+919876543211",
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
    
    db_session.add_all([driver1, driver2])
    db_session.commit()
    
    matching_service = MatchingService(redis_client, db_session)
    
    # Set drivers at different distances
    matching_service.set_driver_available("driver1", 22.7286, 75.8577)  # ~1km
    matching_service.set_driver_available("driver2", 22.7830, 75.8577)  # ~7km
    
    # Broadcast with 5km radius
    result = matching_service.broadcast_ride_request(
        ride_id="ride123",
        pickup_latitude=22.7196,
        pickup_longitude=75.8577,
        destination_latitude=22.7500,
        destination_longitude=75.8700,
        estimated_fare=150.0,
        radius_km=5.0
    )
    
    # Only driver1 should be notified
    assert result["drivers_notified"] == 1
    assert result["notified_drivers"][0]["driver_id"] == "driver1"


def test_broadcast_includes_driver_distance(db_session, redis_client):
    """Test that broadcast includes distance to pickup for each driver."""
    driver = User(
        user_id="driver1",
        phone_number="+919876543210",
        name="Driver One",
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
    
    db_session.add(driver)
    db_session.commit()
    
    matching_service = MatchingService(redis_client, db_session)
    matching_service.set_driver_available("driver1", 22.7286, 75.8577)
    
    result = matching_service.broadcast_ride_request(
        ride_id="ride123",
        pickup_latitude=22.7196,
        pickup_longitude=75.8577,
        destination_latitude=22.7500,
        destination_longitude=75.8700,
        estimated_fare=150.0,
        radius_km=5.0
    )
    
    # Verify distance is included
    assert "distance_km" in result["notified_drivers"][0]
    assert result["notified_drivers"][0]["distance_km"] > 0


def test_cancel_broadcast(db_session, redis_client):
    """Test that broadcast can be cancelled."""
    driver = User(
        user_id="driver1",
        phone_number="+919876543210",
        name="Driver One",
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
    
    db_session.add(driver)
    db_session.commit()
    
    matching_service = MatchingService(redis_client, db_session)
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
    
    # Cancel broadcast
    result = matching_service.cancel_broadcast("ride123")
    
    assert result["status"] == "success"
    assert "cancelled" in result["message"].lower()
    
    # Verify broadcast status is updated
    broadcast_details = matching_service.get_broadcast_details("ride123")
    assert broadcast_details["status"] == "cancelled"
    assert "cancelled_at" in broadcast_details


def test_broadcast_with_no_available_drivers(db_session, redis_client):
    """Test broadcast when no drivers are available."""
    matching_service = MatchingService(redis_client, db_session)
    
    # Broadcast with no available drivers
    result = matching_service.broadcast_ride_request(
        ride_id="ride123",
        pickup_latitude=22.7196,
        pickup_longitude=75.8577,
        destination_latitude=22.7500,
        destination_longitude=75.8700,
        estimated_fare=150.0,
        radius_km=5.0
    )
    
    assert result["status"] == "success"
    assert result["drivers_notified"] == 0
    assert len(result["notified_drivers"]) == 0


def test_broadcast_with_custom_radius(db_session, redis_client):
    """Test broadcast with custom radius parameter."""
    driver = User(
        user_id="driver1",
        phone_number="+919876543210",
        name="Driver One",
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
    
    db_session.add(driver)
    db_session.commit()
    
    matching_service = MatchingService(redis_client, db_session)
    matching_service.set_driver_available("driver1", 22.7830, 75.8577)  # ~7km away
    
    # Broadcast with 10km radius
    result = matching_service.broadcast_ride_request(
        ride_id="ride123",
        pickup_latitude=22.7196,
        pickup_longitude=75.8577,
        destination_latitude=22.7500,
        destination_longitude=75.8700,
        estimated_fare=150.0,
        radius_km=10.0
    )
    
    assert result["status"] == "success"
    assert result["broadcast_radius_km"] == 10.0
    assert result["drivers_notified"] == 1


# Property-Based Tests
from hypothesis import given, strategies as st, assume, settings, HealthCheck


@settings(
    max_examples=50,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@given(
    num_drivers=st.integers(min_value=0, max_value=20),
    pickup_lat=st.floats(min_value=22.6, max_value=22.8),
    pickup_lon=st.floats(min_value=75.7, max_value=75.9),
    dest_lat=st.floats(min_value=22.6, max_value=22.8),
    dest_lon=st.floats(min_value=75.7, max_value=75.9),
    estimated_fare=st.floats(min_value=30.0, max_value=500.0),
    radius_km=st.floats(min_value=1.0, max_value=15.0)
)
def test_property_ride_request_broadcasting(
    db_session,
    redis_client,
    num_drivers,
    pickup_lat,
    pickup_lon,
    dest_lat,
    dest_lon,
    estimated_fare,
    radius_km
):
    """
    Property 10: Ride request broadcasting
    
    For any confirmed ride request, the system should broadcast to available drivers
    and record which drivers were notified.
    
    **Validates: Requirements 2.3**
    """
    # Assume valid coordinates (not NaN or infinite)
    assume(not (any([
        abs(pickup_lat) == float('inf'),
        abs(pickup_lon) == float('inf'),
        abs(dest_lat) == float('inf'),
        abs(dest_lon) == float('inf'),
        pickup_lat != pickup_lat,  # NaN check
        pickup_lon != pickup_lon,
        dest_lat != dest_lat,
        dest_lon != dest_lon
    ])))
    
    # Generate unique test ID for this run to avoid conflicts
    import uuid
    test_run_id = str(uuid.uuid4())[:8]
    
    matching_service = MatchingService(redis_client, db_session)
    
    # Create drivers at various distances from pickup
    created_drivers = []
    drivers_within_radius = []
    
    for i in range(num_drivers):
        driver_id = f"driver_pbt_{test_run_id}_{i}"
        
        # Create driver in database
        driver = User(
            user_id=driver_id,
            phone_number=f"+91987654{test_run_id[:4]}{i:02d}",
            name=f"Driver {test_run_id}_{i}",
            email=f"driver{test_run_id}_{i}@test.com",
            user_type="driver",
            phone_verified=True,
            password_hash="hashed_password"
        )
        driver.driver_profile = DriverProfile(
            driver_id=driver_id,
            license_number=f"DL{test_run_id}{i:06d}",
            vehicle_registration=f"MP09{test_run_id[:2]}{i:04d}",
            vehicle_make="Maruti",
            vehicle_model="Swift",
            vehicle_color="White",
            insurance_expiry=datetime.utcnow() + timedelta(days=365),
            status="available"
        )
        
        db_session.add(driver)
        created_drivers.append(driver_id)
    
    # Commit all drivers to database before setting availability
    db_session.commit()
    
    # Now set driver availability and calculate distances
    for i in range(num_drivers):
        driver_id = f"driver_pbt_{test_run_id}_{i}"
        
        # Place driver at a location relative to pickup
        # Vary the distance to test radius filtering
        lat_offset = (i % 10 - 5) * 0.01  # Varies roughly ±0.05 degrees (~5km)
        lon_offset = (i % 7 - 3) * 0.01
        driver_lat = pickup_lat + lat_offset
        driver_lon = pickup_lon + lon_offset
        
        # Ensure driver location is within Indore boundaries
        driver_lat = max(22.6, min(22.8, driver_lat))
        driver_lon = max(75.7, min(75.9, driver_lon))
        
        # Set driver as available
        matching_service.set_driver_available(driver_id, driver_lat, driver_lon)
        
        # Calculate if this driver should be within radius
        distance = calculate_distance(pickup_lat, pickup_lon, driver_lat, driver_lon)
        if distance <= radius_km:
            drivers_within_radius.append(driver_id)
    
    # Generate unique ride ID
    ride_id = f"ride_pbt_{test_run_id}"
    
    # Broadcast ride request
    result = matching_service.broadcast_ride_request(
        ride_id=ride_id,
        pickup_latitude=pickup_lat,
        pickup_longitude=pickup_lon,
        destination_latitude=dest_lat,
        destination_longitude=dest_lon,
        estimated_fare=estimated_fare,
        radius_km=radius_km
    )
    
    # Property assertions:
    # 1. Broadcast should succeed
    assert result["status"] == "success"
    assert result["ride_id"] == ride_id
    
    # 2. System should record which drivers were notified
    broadcast_details = matching_service.get_broadcast_details(ride_id)
    assert broadcast_details is not None
    assert "notified_drivers" in broadcast_details
    assert isinstance(broadcast_details["notified_drivers"], list)
    
    # 3. The number of notified drivers should match drivers within radius
    assert result["drivers_notified"] == len(drivers_within_radius)
    assert len(result["notified_drivers"]) == len(drivers_within_radius)
    
    # 4. All notified drivers should be in the recorded list
    notified_driver_ids = [d["driver_id"] for d in result["notified_drivers"]]
    for driver_id in notified_driver_ids:
        assert driver_id in broadcast_details["notified_drivers"]
    
    # 5. Only drivers within radius should be notified
    for driver_id in notified_driver_ids:
        assert driver_id in drivers_within_radius
    
    # 6. Broadcast details should be stored with all required information
    assert broadcast_details["pickup_latitude"] == pickup_lat
    assert broadcast_details["pickup_longitude"] == pickup_lon
    assert broadcast_details["destination_latitude"] == dest_lat
    assert broadcast_details["destination_longitude"] == dest_lon
    assert broadcast_details["estimated_fare"] == estimated_fare
    assert broadcast_details["radius_km"] == radius_km
    assert broadcast_details["status"] == "active"
    assert "broadcast_time" in broadcast_details
    
    # Cleanup
    try:
        for driver_id in created_drivers:
            matching_service.set_driver_unavailable(driver_id)
            driver = db_session.query(User).filter(User.user_id == driver_id).first()
            if driver:
                db_session.delete(driver)
        db_session.commit()
    except Exception:
        db_session.rollback()
