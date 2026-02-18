"""
Tests for ride cancellation logic.

This module tests the cancel_ride function and cancellation endpoint.
Validates Requirements: 15.1, 15.2, 15.3, 15.7
"""

import pytest
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.ride import Ride, RideStatus, PaymentStatus
from app.services.ride_service import cancel_ride


@pytest.fixture
def sample_requested_ride(db_session):
    """Create a sample ride in REQUESTED status (pre-match)."""
    ride = Ride(
        ride_id="test_ride_cancel_001",
        rider_id="rider_123",
        driver_id=None,  # No driver matched yet
        status=RideStatus.REQUESTED,
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
        requested_at=datetime.utcnow()
    )
    db_session.add(ride)
    db_session.commit()
    db_session.refresh(ride)
    return ride


@pytest.fixture
def sample_matched_ride(db_session):
    """Create a sample ride in MATCHED status (post-match)."""
    ride = Ride(
        ride_id="test_ride_cancel_002",
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
        requested_at=datetime.utcnow(),
        matched_at=datetime.utcnow()
    )
    db_session.add(ride)
    db_session.commit()
    db_session.refresh(ride)
    return ride


@pytest.fixture
def sample_driver_arriving_ride(db_session):
    """Create a sample ride in DRIVER_ARRIVING status."""
    ride = Ride(
        ride_id="test_ride_cancel_003",
        rider_id="rider_123",
        driver_id="driver_456",
        status=RideStatus.DRIVER_ARRIVING,
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
        requested_at=datetime.utcnow(),
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
        ride_id="test_ride_cancel_004",
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
        requested_at=datetime.utcnow(),
        matched_at=datetime.utcnow(),
        pickup_time=datetime.utcnow(),
        start_time=datetime.utcnow()
    )
    db_session.add(ride)
    db_session.commit()
    db_session.refresh(ride)
    return ride


class TestPreMatchCancellation:
    """Test cases for pre-match cancellation (Requirement 15.1)."""
    
    def test_rider_cancels_requested_ride_no_fee(self, db_session, sample_requested_ride):
        """Test rider cancelling a REQUESTED ride - should have no fee."""
        # Act
        cancelled_ride = cancel_ride(
            ride_id=sample_requested_ride.ride_id,
            user_id=sample_requested_ride.rider_id,
            cancellation_reason="Changed my mind",
            db=db_session
        )
        
        # Assert
        assert cancelled_ride.status == RideStatus.CANCELLED
        assert cancelled_ride.cancelled_by == sample_requested_ride.rider_id
        assert cancelled_ride.cancellation_fee == 0.0
        assert cancelled_ride.cancellation_reason == "Changed my mind"
        assert cancelled_ride.cancellation_timestamp is not None
        assert isinstance(cancelled_ride.cancellation_timestamp, datetime)
    
    def test_rider_cancels_requested_ride_without_reason(self, db_session, sample_requested_ride):
        """Test rider cancelling without providing a reason."""
        # Act
        cancelled_ride = cancel_ride(
            ride_id=sample_requested_ride.ride_id,
            user_id=sample_requested_ride.rider_id,
            cancellation_reason=None,
            db=db_session
        )
        
        # Assert
        assert cancelled_ride.status == RideStatus.CANCELLED
        assert cancelled_ride.cancellation_fee == 0.0
        assert cancelled_ride.cancellation_reason is None


class TestPostMatchCancellation:
    """Test cases for post-match cancellation (Requirements 15.2, 15.3)."""
    
    def test_rider_cancels_matched_ride_with_fee(self, db_session, sample_matched_ride):
        """Test rider cancelling a MATCHED ride - should charge ₹20 fee."""
        # Act
        cancelled_ride = cancel_ride(
            ride_id=sample_matched_ride.ride_id,
            user_id=sample_matched_ride.rider_id,
            cancellation_reason="Emergency came up",
            db=db_session
        )
        
        # Assert
        assert cancelled_ride.status == RideStatus.CANCELLED
        assert cancelled_ride.cancelled_by == sample_matched_ride.rider_id
        assert cancelled_ride.cancellation_fee == 20.0
        assert cancelled_ride.cancellation_reason == "Emergency came up"
        assert cancelled_ride.cancellation_timestamp is not None
    
    def test_rider_cancels_driver_arriving_ride_with_fee(self, db_session, sample_driver_arriving_ride):
        """Test rider cancelling a DRIVER_ARRIVING ride - should charge ₹20 fee."""
        # Act
        cancelled_ride = cancel_ride(
            ride_id=sample_driver_arriving_ride.ride_id,
            user_id=sample_driver_arriving_ride.rider_id,
            cancellation_reason="Driver taking too long",
            db=db_session
        )
        
        # Assert
        assert cancelled_ride.status == RideStatus.CANCELLED
        assert cancelled_ride.cancelled_by == sample_driver_arriving_ride.rider_id
        assert cancelled_ride.cancellation_fee == 20.0
    
    def test_driver_cancels_matched_ride_no_fee(self, db_session, sample_matched_ride):
        """Test driver cancelling a MATCHED ride - should have no fee."""
        # Act
        cancelled_ride = cancel_ride(
            ride_id=sample_matched_ride.ride_id,
            user_id=sample_matched_ride.driver_id,
            cancellation_reason="Vehicle issue",
            db=db_session
        )
        
        # Assert
        assert cancelled_ride.status == RideStatus.CANCELLED
        assert cancelled_ride.cancelled_by == sample_matched_ride.driver_id
        assert cancelled_ride.cancellation_fee == 0.0
        assert cancelled_ride.cancellation_reason == "Vehicle issue"
    
    def test_driver_cancels_driver_arriving_ride_no_fee(self, db_session, sample_driver_arriving_ride):
        """Test driver cancelling a DRIVER_ARRIVING ride - should have no fee."""
        # Act
        cancelled_ride = cancel_ride(
            ride_id=sample_driver_arriving_ride.ride_id,
            user_id=sample_driver_arriving_ride.driver_id,
            cancellation_reason="Traffic jam",
            db=db_session
        )
        
        # Assert
        assert cancelled_ride.status == RideStatus.CANCELLED
        assert cancelled_ride.cancelled_by == sample_driver_arriving_ride.driver_id
        assert cancelled_ride.cancellation_fee == 0.0


class TestInProgressCancellationRestriction:
    """Test cases for in-progress cancellation restriction (Requirement 15.7)."""
    
    def test_cannot_cancel_in_progress_ride_by_rider(self, db_session, sample_in_progress_ride):
        """Test that rider cannot cancel an IN_PROGRESS ride."""
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            cancel_ride(
                ride_id=sample_in_progress_ride.ride_id,
                user_id=sample_in_progress_ride.rider_id,
                cancellation_reason="Want to cancel",
                db=db_session
            )
        
        assert exc_info.value.status_code == 422
        assert "cannot cancel" in str(exc_info.value.detail).lower()
        assert "in_progress" in str(exc_info.value.detail).lower()
    
    def test_cannot_cancel_in_progress_ride_by_driver(self, db_session, sample_in_progress_ride):
        """Test that driver cannot cancel an IN_PROGRESS ride."""
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            cancel_ride(
                ride_id=sample_in_progress_ride.ride_id,
                user_id=sample_in_progress_ride.driver_id,
                cancellation_reason="Want to cancel",
                db=db_session
            )
        
        assert exc_info.value.status_code == 422
        assert "cannot cancel" in str(exc_info.value.detail).lower()
    
    def test_cannot_cancel_completed_ride(self, db_session):
        """Test that completed rides cannot be cancelled."""
        # Arrange
        ride = Ride(
            ride_id="test_ride_cancel_005",
            rider_id="rider_123",
            driver_id="driver_456",
            status=RideStatus.COMPLETED,
            pickup_location={"latitude": 22.7196, "longitude": 75.8577, "address": "Test"},
            destination={"latitude": 22.7520, "longitude": 75.8937, "address": "Test"},
            estimated_fare=96.0,
            final_fare=96.0,
            fare_breakdown={"base": 30.0, "per_km": 12.0, "distance": 5.5, "surge": 1.0},
            payment_status=PaymentStatus.COMPLETED,
            requested_at=datetime.utcnow(),
            matched_at=datetime.utcnow(),
            start_time=datetime.utcnow(),
            completed_at=datetime.utcnow()
        )
        db_session.add(ride)
        db_session.commit()
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            cancel_ride(
                ride_id=ride.ride_id,
                user_id=ride.rider_id,
                cancellation_reason="Want to cancel",
                db=db_session
            )
        
        assert exc_info.value.status_code == 422
        assert "cannot cancel" in str(exc_info.value.detail).lower()
    
    def test_cannot_cancel_already_cancelled_ride(self, db_session):
        """Test that already cancelled rides cannot be cancelled again."""
        # Arrange
        ride = Ride(
            ride_id="test_ride_cancel_006",
            rider_id="rider_123",
            driver_id="driver_456",
            status=RideStatus.CANCELLED,
            pickup_location={"latitude": 22.7196, "longitude": 75.8577, "address": "Test"},
            destination={"latitude": 22.7520, "longitude": 75.8937, "address": "Test"},
            estimated_fare=96.0,
            fare_breakdown={"base": 30.0, "per_km": 12.0, "distance": 5.5, "surge": 1.0},
            payment_status=PaymentStatus.PENDING,
            requested_at=datetime.utcnow(),
            matched_at=datetime.utcnow(),
            cancelled_by="rider_123",
            cancellation_fee=20.0,
            cancellation_timestamp=datetime.utcnow()
        )
        db_session.add(ride)
        db_session.commit()
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            cancel_ride(
                ride_id=ride.ride_id,
                user_id=ride.rider_id,
                cancellation_reason="Want to cancel again",
                db=db_session
            )
        
        assert exc_info.value.status_code == 422
        assert "cannot cancel" in str(exc_info.value.detail).lower()


class TestCancellationAuthorization:
    """Test cases for cancellation authorization."""
    
    def test_unauthorized_user_cannot_cancel(self, db_session, sample_matched_ride):
        """Test that a user not involved in the ride cannot cancel it."""
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            cancel_ride(
                ride_id=sample_matched_ride.ride_id,
                user_id="unauthorized_user_789",
                cancellation_reason="Trying to cancel",
                db=db_session
            )
        
        assert exc_info.value.status_code == 403
        assert "not authorized" in str(exc_info.value.detail).lower()
    
    def test_ride_not_found(self, db_session):
        """Test cancelling a non-existent ride."""
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            cancel_ride(
                ride_id="nonexistent_ride",
                user_id="rider_123",
                cancellation_reason="Trying to cancel",
                db=db_session
            )
        
        assert exc_info.value.status_code == 404
        assert "not found" in str(exc_info.value.detail).lower()


class TestCancellationEdgeCases:
    """Test edge cases for cancellation logic."""
    
    def test_cancellation_with_very_long_reason(self, db_session, sample_requested_ride):
        """Test cancellation with a long reason string."""
        # Arrange
        long_reason = "A" * 500  # 500 characters
        
        # Act
        cancelled_ride = cancel_ride(
            ride_id=sample_requested_ride.ride_id,
            user_id=sample_requested_ride.rider_id,
            cancellation_reason=long_reason,
            db=db_session
        )
        
        # Assert
        assert cancelled_ride.status == RideStatus.CANCELLED
        assert cancelled_ride.cancellation_reason == long_reason
        assert len(cancelled_ride.cancellation_reason) == 500
    
    def test_cancellation_with_empty_string_reason(self, db_session, sample_requested_ride):
        """Test cancellation with empty string as reason."""
        # Act
        cancelled_ride = cancel_ride(
            ride_id=sample_requested_ride.ride_id,
            user_id=sample_requested_ride.rider_id,
            cancellation_reason="",
            db=db_session
        )
        
        # Assert
        assert cancelled_ride.status == RideStatus.CANCELLED
        assert cancelled_ride.cancellation_reason == ""
    
    def test_cancellation_preserves_other_ride_data(self, db_session, sample_matched_ride):
        """Test that cancellation doesn't modify other ride fields."""
        # Arrange
        original_rider_id = sample_matched_ride.rider_id
        original_driver_id = sample_matched_ride.driver_id
        original_estimated_fare = sample_matched_ride.estimated_fare
        original_pickup = sample_matched_ride.pickup_location
        original_destination = sample_matched_ride.destination
        original_requested_at = sample_matched_ride.requested_at
        original_matched_at = sample_matched_ride.matched_at
        
        # Act
        cancelled_ride = cancel_ride(
            ride_id=sample_matched_ride.ride_id,
            user_id=sample_matched_ride.rider_id,
            cancellation_reason="Test",
            db=db_session
        )
        
        # Assert - verify other fields unchanged
        assert cancelled_ride.rider_id == original_rider_id
        assert cancelled_ride.driver_id == original_driver_id
        assert cancelled_ride.estimated_fare == original_estimated_fare
        assert cancelled_ride.pickup_location == original_pickup
        assert cancelled_ride.destination == original_destination
        assert cancelled_ride.requested_at == original_requested_at
        assert cancelled_ride.matched_at == original_matched_at


class TestCancellationFeeCalculation:
    """Test specific cancellation fee calculations."""
    
    def test_exact_fee_for_rider_post_match(self, db_session, sample_matched_ride):
        """Test that rider cancellation fee is exactly ₹20 after match."""
        # Act
        cancelled_ride = cancel_ride(
            ride_id=sample_matched_ride.ride_id,
            user_id=sample_matched_ride.rider_id,
            cancellation_reason="Test",
            db=db_session
        )
        
        # Assert - exact fee check
        assert cancelled_ride.cancellation_fee == 20.0
        assert isinstance(cancelled_ride.cancellation_fee, float)
    
    def test_zero_fee_for_rider_pre_match(self, db_session, sample_requested_ride):
        """Test that rider cancellation fee is exactly ₹0 before match."""
        # Act
        cancelled_ride = cancel_ride(
            ride_id=sample_requested_ride.ride_id,
            user_id=sample_requested_ride.rider_id,
            cancellation_reason="Test",
            db=db_session
        )
        
        # Assert - exact fee check
        assert cancelled_ride.cancellation_fee == 0.0
        assert isinstance(cancelled_ride.cancellation_fee, float)
    
    def test_zero_fee_for_driver_cancellation(self, db_session, sample_matched_ride):
        """Test that driver cancellation always has ₹0 fee."""
        # Act
        cancelled_ride = cancel_ride(
            ride_id=sample_matched_ride.ride_id,
            user_id=sample_matched_ride.driver_id,
            cancellation_reason="Test",
            db=db_session
        )
        
        # Assert - exact fee check
        assert cancelled_ride.cancellation_fee == 0.0
        assert isinstance(cancelled_ride.cancellation_fee, float)
