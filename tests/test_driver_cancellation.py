"""
Tests for driver cancellation handling.

Tests cover:
- Driver cancellation of matched rides
- Cancellation count tracking
- Driver suspension after exceeding limit
- Ride re-broadcasting after cancellation
- Daily cancellation count reset
"""
import pytest
from datetime import datetime, timedelta
from uuid import uuid4
from app.services.matching_service import MatchingService
from app.models.ride import Ride, RideStatus, PaymentStatus
from app.models.user import User, UserType, DriverProfile, DriverStatus


@pytest.fixture
def driver_with_profile(db_session):
    """Create a driver user with profile."""
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
        status=DriverStatus.BUSY,
        cancellation_count=0,
        last_cancellation_reset=datetime.utcnow()
    )
    
    driver.driver_profile = driver_profile
    db_session.add(driver)
    db_session.commit()
    
    return driver


@pytest.fixture
def matched_ride(db_session, driver_with_profile):
    """Create a matched ride."""
    rider_id = str(uuid4())
    rider = User(
        user_id=rider_id,
        phone_number=f"+91{uuid4().hex[:10]}",
        phone_verified=True,
        name="Test Rider",
        email=f"rider_{uuid4().hex[:8]}@test.com",
        user_type=UserType.RIDER,
        password_hash="hashed_password"
    )
    db_session.add(rider)
    
    ride_id = str(uuid4())
    ride = Ride(
        ride_id=ride_id,
        rider_id=rider_id,
        driver_id=driver_with_profile.user_id,
        status=RideStatus.MATCHED,
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
        requested_at=datetime.utcnow(),
        matched_at=datetime.utcnow(),
        estimated_fare=120.0,
        fare_breakdown={
            "base_fare": 30.0,
            "distance_charge": 90.0,
            "surge_multiplier": 1.0
        },
        payment_status=PaymentStatus.PENDING
    )
    
    db_session.add(ride)
    db_session.commit()
    
    return ride


def test_driver_cancellation_success(redis_client, db_session, matched_ride, driver_with_profile):
    """Test successful driver cancellation of a matched ride."""
    matching_service = MatchingService(redis_client, db_session)
    
    # Set driver as available in Redis for re-broadcast
    matching_service.set_driver_available(
        driver_with_profile.user_id,
        22.7196,
        75.8577
    )
    
    result = matching_service.handle_driver_cancellation(
        ride_id=matched_ride.ride_id,
        driver_id=driver_with_profile.user_id,
        reason="Emergency"
    )
    
    assert result["status"] == "success"
    assert result["ride_id"] == matched_ride.ride_id
    assert result["driver_id"] == driver_with_profile.user_id
    assert result["cancellation_count"] == 1
    assert result["driver_suspended"] is False
    assert result["ride_re_broadcasted"] is True
    
    # Verify ride status updated
    db_session.refresh(matched_ride)
    assert matched_ride.status == RideStatus.REQUESTED
    assert matched_ride.driver_id is None
    assert matched_ride.cancelled_by == driver_with_profile.user_id
    assert matched_ride.cancellation_reason == "Emergency"
    
    # Verify driver profile updated
    db_session.refresh(driver_with_profile.driver_profile)
    assert driver_with_profile.driver_profile.cancellation_count == 1


def test_driver_cancellation_increments_count(redis_client, db_session, driver_with_profile):
    """Test that multiple cancellations increment the count correctly."""
    matching_service = MatchingService(redis_client, db_session)
    
    # Create and cancel 3 rides
    for i in range(3):
        rider_id = str(uuid4())
        rider = User(
            user_id=rider_id,
            phone_number=f"+91{uuid4().hex[:10]}",
            phone_verified=True,
            name=f"Test Rider {i}",
            email=f"rider_{i}_{uuid4().hex[:8]}@test.com",
            user_type=UserType.RIDER,
            password_hash="hashed_password"
        )
        db_session.add(rider)
        
        ride = Ride(
            ride_id=str(uuid4()),
            rider_id=rider_id,
            driver_id=driver_with_profile.user_id,
            status=RideStatus.MATCHED,
            pickup_location={"latitude": 22.7196, "longitude": 75.8577, "address": "Test"},
            destination={"latitude": 22.7532, "longitude": 75.8937, "address": "Test"},
            requested_at=datetime.utcnow(),
            matched_at=datetime.utcnow(),
            estimated_fare=100.0,
            fare_breakdown={"base_fare": 30.0, "distance_charge": 70.0, "surge_multiplier": 1.0},
            payment_status=PaymentStatus.PENDING
        )
        db_session.add(ride)
        db_session.commit()
        
        result = matching_service.handle_driver_cancellation(
            ride_id=ride.ride_id,
            driver_id=driver_with_profile.user_id
        )
        
        assert result["status"] == "success"
        assert result["cancellation_count"] == i + 1
    
    # Verify final count
    db_session.refresh(driver_with_profile.driver_profile)
    assert driver_with_profile.driver_profile.cancellation_count == 3


def test_driver_suspension_after_exceeding_limit(redis_client, db_session, driver_with_profile):
    """Test that driver is suspended after 4th cancellation in a day."""
    matching_service = MatchingService(redis_client, db_session)
    
    # Create and cancel 4 rides
    for i in range(4):
        rider_id = str(uuid4())
        rider = User(
            user_id=rider_id,
            phone_number=f"+91{uuid4().hex[:10]}",
            phone_verified=True,
            name=f"Test Rider {i}",
            email=f"rider_{i}_{uuid4().hex[:8]}@test.com",
            user_type=UserType.RIDER,
            password_hash="hashed_password"
        )
        db_session.add(rider)
        
        ride = Ride(
            ride_id=str(uuid4()),
            rider_id=rider_id,
            driver_id=driver_with_profile.user_id,
            status=RideStatus.MATCHED,
            pickup_location={"latitude": 22.7196, "longitude": 75.8577, "address": "Test"},
            destination={"latitude": 22.7532, "longitude": 75.8937, "address": "Test"},
            requested_at=datetime.utcnow(),
            matched_at=datetime.utcnow(),
            estimated_fare=100.0,
            fare_breakdown={"base_fare": 30.0, "distance_charge": 70.0, "surge_multiplier": 1.0},
            payment_status=PaymentStatus.PENDING
        )
        db_session.add(ride)
        db_session.commit()
        
        result = matching_service.handle_driver_cancellation(
            ride_id=ride.ride_id,
            driver_id=driver_with_profile.user_id
        )
        
        assert result["status"] == "success"
        
        # Check suspension status
        if i < 3:
            assert result["driver_suspended"] is False
        else:
            assert result["driver_suspended"] is True
            assert result["suspension_expires_at"] is not None
    
    # Verify driver is suspended
    db_session.refresh(driver_with_profile.driver_profile)
    assert driver_with_profile.driver_profile.is_suspended is True
    assert driver_with_profile.driver_profile.cancellation_count == 4


def test_cancellation_of_non_matched_ride_fails(redis_client, db_session, matched_ride, driver_with_profile):
    """Test that cancellation fails if ride is not matched to the driver."""
    matching_service = MatchingService(redis_client, db_session)
    
    # Try to cancel with wrong driver ID
    wrong_driver_id = str(uuid4())
    
    result = matching_service.handle_driver_cancellation(
        ride_id=matched_ride.ride_id,
        driver_id=wrong_driver_id
    )
    
    assert result["status"] == "error"
    assert "not assigned to driver" in result["message"]


def test_cancellation_of_in_progress_ride_fails(redis_client, db_session, matched_ride, driver_with_profile):
    """Test that cancellation fails for in-progress rides."""
    matching_service = MatchingService(redis_client, db_session)
    
    # Update ride to in-progress
    matched_ride.status = RideStatus.IN_PROGRESS
    matched_ride.start_time = datetime.utcnow()
    db_session.commit()
    
    result = matching_service.handle_driver_cancellation(
        ride_id=matched_ride.ride_id,
        driver_id=driver_with_profile.user_id
    )
    
    assert result["status"] == "error"
    assert "cannot be cancelled" in result["message"]


def test_daily_cancellation_count_reset(redis_client, db_session, driver_with_profile):
    """Test that cancellation count resets after 24 hours."""
    matching_service = MatchingService(redis_client, db_session)
    
    # Set cancellation count to 2 and last reset to 25 hours ago
    driver_with_profile.driver_profile.cancellation_count = 2
    driver_with_profile.driver_profile.last_cancellation_reset = datetime.utcnow() - timedelta(hours=25)
    db_session.commit()
    
    # Create and cancel a ride
    rider_id = str(uuid4())
    rider = User(
        user_id=rider_id,
        phone_number=f"+91{uuid4().hex[:10]}",
        phone_verified=True,
        name="Test Rider",
        email=f"rider_{uuid4().hex[:8]}@test.com",
        user_type=UserType.RIDER,
        password_hash="hashed_password"
    )
    db_session.add(rider)
    
    ride = Ride(
        ride_id=str(uuid4()),
        rider_id=rider_id,
        driver_id=driver_with_profile.user_id,
        status=RideStatus.MATCHED,
        pickup_location={"latitude": 22.7196, "longitude": 75.8577, "address": "Test"},
        destination={"latitude": 22.7532, "longitude": 75.8937, "address": "Test"},
        requested_at=datetime.utcnow(),
        matched_at=datetime.utcnow(),
        estimated_fare=100.0,
        fare_breakdown={"base_fare": 30.0, "distance_charge": 70.0, "surge_multiplier": 1.0},
        payment_status=PaymentStatus.PENDING
    )
    db_session.add(ride)
    db_session.commit()
    
    result = matching_service.handle_driver_cancellation(
        ride_id=ride.ride_id,
        driver_id=driver_with_profile.user_id
    )
    
    assert result["status"] == "success"
    # Count should be reset to 0 and then incremented to 1
    assert result["cancellation_count"] == 1
    
    db_session.refresh(driver_with_profile.driver_profile)
    assert driver_with_profile.driver_profile.cancellation_count == 1
