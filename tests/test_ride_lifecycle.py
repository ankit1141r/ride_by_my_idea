"""
Tests for ride lifecycle management.

This module tests the ride lifecycle functions: start_ride and complete_ride.
Validates Requirements: 3.3, 5.4
"""

import pytest
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.ride import Ride, RideStatus, PaymentStatus
from app.services.ride_service import start_ride, complete_ride, get_ride_status


@pytest.fixture
def sample_matched_ride(db_session):
    """Create a sample ride in MATCHED status."""
    ride = Ride(
        ride_id="test_ride_001",
        rider_id="rider_123",
        driver_id="driver_456",
        status=RideStatus.MATCHED,
        pickup_location={
            "latitude": 22.7196,
            "longitude": 75.8577,
            "address": "Vijay Nagar, Indore"
        },
        destination={
            "latitude": 22.7520,
            "longitude": 75.8937,
            "address": "Rajwada, Indore"
        },
        estimated_fare=96.0,
        fare_breakdown={
            "base": 30.0,
            "per_km": 12.0,
            "distance": 5.5,
            "surge": 1.0,
            "total": 96.0
        },
        payment_status=PaymentStatus.PENDING,
        matched_at=datetime.utcnow()
    )
    db_session.add(ride)
    db_session.commit()
    db_session.refresh(ride)
    return ride


@pytest.fixture
def sample_in_progress_ride(db_session):
    """Create a sample ride in IN_PROGRESS status."""
    ride = Ride(
        ride_id="test_ride_002",
        rider_id="rider_123",
        driver_id="driver_456",
        status=RideStatus.IN_PROGRESS,
        pickup_location={
            "latitude": 22.7196,
            "longitude": 75.8577,
            "address": "Vijay Nagar, Indore"
        },
        destination={
            "latitude": 22.7520,
            "longitude": 75.8937,
            "address": "Rajwada, Indore"
        },
        estimated_fare=96.0,
        fare_breakdown={
            "base": 30.0,
            "per_km": 12.0,
            "distance": 5.5,
            "surge": 1.0,
            "total": 96.0
        },
        payment_status=PaymentStatus.PENDING,
        matched_at=datetime.utcnow(),
        pickup_time=datetime.utcnow(),
        start_time=datetime.utcnow()
    )
    db_session.add(ride)
    db_session.commit()
    db_session.refresh(ride)
    return ride


class TestStartRide:
    """Test cases for start_ride function."""
    
    def test_start_ride_success(self, db_session, sample_matched_ride):
        """Test successfully starting a matched ride."""
        # Act
        updated_ride = start_ride(
            ride_id=sample_matched_ride.ride_id,
            driver_id=sample_matched_ride.driver_id,
            db=db_session
        )
        
        # Assert
        assert updated_ride.status == RideStatus.IN_PROGRESS
        assert updated_ride.start_time is not None
        assert updated_ride.pickup_time is not None
        assert isinstance(updated_ride.start_time, datetime)
    
    def test_start_ride_from_driver_arriving(self, db_session):
        """Test starting a ride from DRIVER_ARRIVING status."""
        # Arrange
        ride = Ride(
            ride_id="test_ride_003",
            rider_id="rider_123",
            driver_id="driver_456",
            status=RideStatus.DRIVER_ARRIVING,
            pickup_location={"latitude": 22.7196, "longitude": 75.8577, "address": "Test"},
            destination={"latitude": 22.7520, "longitude": 75.8937, "address": "Test"},
            estimated_fare=96.0,
            fare_breakdown={"base": 30.0, "per_km": 12.0, "distance": 5.5, "surge": 1.0},
            payment_status=PaymentStatus.PENDING
        )
        db_session.add(ride)
        db_session.commit()
        
        # Act
        updated_ride = start_ride(
            ride_id=ride.ride_id,
            driver_id=ride.driver_id,
            db=db_session
        )
        
        # Assert
        assert updated_ride.status == RideStatus.IN_PROGRESS
        assert updated_ride.start_time is not None
    
    def test_start_ride_not_found(self, db_session):
        """Test starting a non-existent ride."""
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            start_ride(
                ride_id="nonexistent_ride",
                driver_id="driver_456",
                db=db_session
            )
        
        assert exc_info.value.status_code == 404
        assert "not found" in str(exc_info.value.detail).lower()
    
    def test_start_ride_wrong_driver(self, db_session, sample_matched_ride):
        """Test starting a ride with wrong driver ID."""
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            start_ride(
                ride_id=sample_matched_ride.ride_id,
                driver_id="wrong_driver_789",
                db=db_session
            )
        
        assert exc_info.value.status_code == 403
        assert "does not match" in str(exc_info.value.detail).lower()
    
    def test_start_ride_invalid_status(self, db_session):
        """Test starting a ride with invalid status (e.g., COMPLETED)."""
        # Arrange
        ride = Ride(
            ride_id="test_ride_004",
            rider_id="rider_123",
            driver_id="driver_456",
            status=RideStatus.COMPLETED,
            pickup_location={"latitude": 22.7196, "longitude": 75.8577, "address": "Test"},
            destination={"latitude": 22.7520, "longitude": 75.8937, "address": "Test"},
            estimated_fare=96.0,
            fare_breakdown={"base": 30.0, "per_km": 12.0, "distance": 5.5, "surge": 1.0},
            payment_status=PaymentStatus.PENDING,
            completed_at=datetime.utcnow()
        )
        db_session.add(ride)
        db_session.commit()
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            start_ride(
                ride_id=ride.ride_id,
                driver_id=ride.driver_id,
                db=db_session
            )
        
        assert exc_info.value.status_code == 422
        assert "cannot start" in str(exc_info.value.detail).lower()


class TestCompleteRide:
    """Test cases for complete_ride function."""
    
    def test_complete_ride_success(self, db_session, sample_in_progress_ride):
        """Test successfully completing an in-progress ride."""
        # Act
        updated_ride = complete_ride(
            ride_id=sample_in_progress_ride.ride_id,
            driver_id=sample_in_progress_ride.driver_id,
            actual_distance_km=5.5,
            db=db_session
        )
        
        # Assert
        assert updated_ride.status == RideStatus.COMPLETED
        assert updated_ride.completed_at is not None
        assert updated_ride.final_fare is not None
        assert updated_ride.final_fare > 0
        assert isinstance(updated_ride.completed_at, datetime)
    
    def test_complete_ride_with_fare_protection(self, db_session, sample_in_progress_ride):
        """Test completing a ride where actual fare exceeds 20% of estimated."""
        # Arrange - estimated fare is 96.0 for 5.5km
        # If actual distance is 10km, actual fare would be 30 + 10*12 = 150
        # Difference: (150-96)/96 = 56% > 20%, so should cap at 96
        
        # Act
        updated_ride = complete_ride(
            ride_id=sample_in_progress_ride.ride_id,
            driver_id=sample_in_progress_ride.driver_id,
            actual_distance_km=10.0,
            db=db_session
        )
        
        # Assert - should be capped at estimated fare
        assert updated_ride.final_fare == sample_in_progress_ride.estimated_fare
        assert updated_ride.fare_breakdown["distance"] == 10.0
    
    def test_complete_ride_without_fare_protection(self, db_session, sample_in_progress_ride):
        """Test completing a ride where actual fare is within 20% of estimated."""
        # Arrange - estimated fare is 96.0 for 5.5km
        # If actual distance is 6km, actual fare would be 30 + 6*12 = 102
        # Difference: (102-96)/96 = 6.25% < 20%, so use actual fare
        
        # Act
        updated_ride = complete_ride(
            ride_id=sample_in_progress_ride.ride_id,
            driver_id=sample_in_progress_ride.driver_id,
            actual_distance_km=6.0,
            db=db_session
        )
        
        # Assert - should use actual fare
        expected_fare = 30.0 + 6.0 * 12.0  # 102.0
        assert updated_ride.final_fare == expected_fare
        assert updated_ride.fare_breakdown["distance"] == 6.0
    
    def test_complete_ride_with_actual_route(self, db_session, sample_in_progress_ride):
        """Test completing a ride with actual route data."""
        # Arrange
        actual_route = [
            {"latitude": 22.7196, "longitude": 75.8577, "timestamp": "2024-01-15T10:00:00Z"},
            {"latitude": 22.7300, "longitude": 75.8700, "timestamp": "2024-01-15T10:05:00Z"},
            {"latitude": 22.7520, "longitude": 75.8937, "timestamp": "2024-01-15T10:10:00Z"}
        ]
        
        # Act
        updated_ride = complete_ride(
            ride_id=sample_in_progress_ride.ride_id,
            driver_id=sample_in_progress_ride.driver_id,
            actual_distance_km=5.5,
            db=db_session,
            actual_route=actual_route
        )
        
        # Assert
        assert updated_ride.actual_route is not None
        assert len(updated_ride.actual_route) == 3
        assert updated_ride.actual_route == actual_route
    
    def test_complete_ride_not_found(self, db_session):
        """Test completing a non-existent ride."""
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            complete_ride(
                ride_id="nonexistent_ride",
                driver_id="driver_456",
                actual_distance_km=5.5,
                db=db_session
            )
        
        assert exc_info.value.status_code == 404
        assert "not found" in str(exc_info.value.detail).lower()
    
    def test_complete_ride_wrong_driver(self, db_session, sample_in_progress_ride):
        """Test completing a ride with wrong driver ID."""
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            complete_ride(
                ride_id=sample_in_progress_ride.ride_id,
                driver_id="wrong_driver_789",
                actual_distance_km=5.5,
                db=db_session
            )
        
        assert exc_info.value.status_code == 403
        assert "does not match" in str(exc_info.value.detail).lower()
    
    def test_complete_ride_invalid_status(self, db_session, sample_matched_ride):
        """Test completing a ride with invalid status (e.g., MATCHED)."""
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            complete_ride(
                ride_id=sample_matched_ride.ride_id,
                driver_id=sample_matched_ride.driver_id,
                actual_distance_km=5.5,
                db=db_session
            )
        
        assert exc_info.value.status_code == 422
        assert "cannot complete" in str(exc_info.value.detail).lower()
    
    def test_complete_ride_negative_distance(self, db_session, sample_in_progress_ride):
        """Test completing a ride with negative distance."""
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            complete_ride(
                ride_id=sample_in_progress_ride.ride_id,
                driver_id=sample_in_progress_ride.driver_id,
                actual_distance_km=-5.0,
                db=db_session
            )
        
        assert exc_info.value.status_code == 400
        assert "non-negative" in str(exc_info.value.detail).lower()
    
    def test_complete_ride_zero_distance(self, db_session, sample_in_progress_ride):
        """Test completing a ride with zero distance (edge case)."""
        # Act
        updated_ride = complete_ride(
            ride_id=sample_in_progress_ride.ride_id,
            driver_id=sample_in_progress_ride.driver_id,
            actual_distance_km=0.0,
            db=db_session
        )
        
        # Assert - actual fare would be 30 (base only), but estimated is 96
        # Difference is 68.75% > 20%, so fare protection caps at estimated fare
        assert updated_ride.final_fare == sample_in_progress_ride.estimated_fare
        assert updated_ride.status == RideStatus.COMPLETED


class TestGetRideStatus:
    """Test cases for get_ride_status function."""
    
    def test_get_ride_status_success(self, db_session, sample_matched_ride):
        """Test getting status of an existing ride."""
        # Act
        status = get_ride_status(
            ride_id=sample_matched_ride.ride_id,
            db=db_session
        )
        
        # Assert
        assert status["ride_id"] == sample_matched_ride.ride_id
        assert status["status"] == RideStatus.MATCHED.value
        assert status["rider_id"] == sample_matched_ride.rider_id
        assert status["driver_id"] == sample_matched_ride.driver_id
        assert status["estimated_fare"] == sample_matched_ride.estimated_fare
    
    def test_get_ride_status_not_found(self, db_session):
        """Test getting status of non-existent ride."""
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            get_ride_status(
                ride_id="nonexistent_ride",
                db=db_session
            )
        
        assert exc_info.value.status_code == 404
        assert "not found" in str(exc_info.value.detail).lower()


class TestRideLifecycleFlow:
    """Integration tests for complete ride lifecycle."""
    
    def test_complete_lifecycle_matched_to_completed(self, db_session, sample_matched_ride):
        """Test complete flow: MATCHED -> IN_PROGRESS -> COMPLETED."""
        # Step 1: Start the ride
        started_ride = start_ride(
            ride_id=sample_matched_ride.ride_id,
            driver_id=sample_matched_ride.driver_id,
            db=db_session
        )
        assert started_ride.status == RideStatus.IN_PROGRESS
        assert started_ride.start_time is not None
        
        # Step 2: Complete the ride
        completed_ride = complete_ride(
            ride_id=sample_matched_ride.ride_id,
            driver_id=sample_matched_ride.driver_id,
            actual_distance_km=5.5,
            db=db_session
        )
        assert completed_ride.status == RideStatus.COMPLETED
        assert completed_ride.completed_at is not None
        assert completed_ride.final_fare is not None
        
        # Verify timestamps are in correct order
        assert completed_ride.matched_at < completed_ride.start_time
        assert completed_ride.start_time < completed_ride.completed_at
