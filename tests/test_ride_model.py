"""
Tests for the Ride model structure and methods.
"""
import pytest
from app.models.ride import Ride, RideStatus, PaymentStatus


def test_ride_status_enum():
    """Test that RideStatus enum has all required values."""
    assert RideStatus.REQUESTED == "requested"
    assert RideStatus.MATCHED == "matched"
    assert RideStatus.DRIVER_ARRIVING == "driver_arriving"
    assert RideStatus.IN_PROGRESS == "in_progress"
    assert RideStatus.COMPLETED == "completed"
    assert RideStatus.CANCELLED == "cancelled"


def test_payment_status_enum():
    """Test that PaymentStatus enum has all required values."""
    assert PaymentStatus.PENDING == "pending"
    assert PaymentStatus.COMPLETED == "completed"
    assert PaymentStatus.FAILED == "failed"


def test_ride_is_cancellable():
    """Test the is_cancellable method."""
    ride = Ride()
    
    # Cancellable statuses
    ride.status = RideStatus.REQUESTED
    assert ride.is_cancellable() is True
    
    ride.status = RideStatus.MATCHED
    assert ride.is_cancellable() is True
    
    ride.status = RideStatus.DRIVER_ARRIVING
    assert ride.is_cancellable() is True
    
    # Non-cancellable statuses
    ride.status = RideStatus.IN_PROGRESS
    assert ride.is_cancellable() is False
    
    ride.status = RideStatus.COMPLETED
    assert ride.is_cancellable() is False
    
    ride.status = RideStatus.CANCELLED
    assert ride.is_cancellable() is False


def test_ride_can_transition_to():
    """Test the can_transition_to method for valid state transitions."""
    ride = Ride()
    
    # From REQUESTED
    ride.status = RideStatus.REQUESTED
    assert ride.can_transition_to(RideStatus.MATCHED) is True
    assert ride.can_transition_to(RideStatus.CANCELLED) is True
    assert ride.can_transition_to(RideStatus.IN_PROGRESS) is False
    
    # From MATCHED
    ride.status = RideStatus.MATCHED
    assert ride.can_transition_to(RideStatus.DRIVER_ARRIVING) is True
    assert ride.can_transition_to(RideStatus.CANCELLED) is True
    assert ride.can_transition_to(RideStatus.COMPLETED) is False
    
    # From DRIVER_ARRIVING
    ride.status = RideStatus.DRIVER_ARRIVING
    assert ride.can_transition_to(RideStatus.IN_PROGRESS) is True
    assert ride.can_transition_to(RideStatus.CANCELLED) is True
    assert ride.can_transition_to(RideStatus.MATCHED) is False
    
    # From IN_PROGRESS
    ride.status = RideStatus.IN_PROGRESS
    assert ride.can_transition_to(RideStatus.COMPLETED) is True
    assert ride.can_transition_to(RideStatus.CANCELLED) is False
    
    # From COMPLETED (no transitions allowed)
    ride.status = RideStatus.COMPLETED
    assert ride.can_transition_to(RideStatus.REQUESTED) is False
    assert ride.can_transition_to(RideStatus.CANCELLED) is False
    
    # From CANCELLED (no transitions allowed)
    ride.status = RideStatus.CANCELLED
    assert ride.can_transition_to(RideStatus.REQUESTED) is False
    assert ride.can_transition_to(RideStatus.COMPLETED) is False


def test_ride_model_has_required_fields():
    """Test that Ride model has all required fields from the design."""
    ride = Ride()
    
    # Check that all required attributes exist
    assert hasattr(ride, 'ride_id')
    assert hasattr(ride, 'rider_id')
    assert hasattr(ride, 'driver_id')
    assert hasattr(ride, 'status')
    
    # Location fields
    assert hasattr(ride, 'pickup_location')
    assert hasattr(ride, 'destination')
    assert hasattr(ride, 'actual_route')
    
    # Timing fields
    assert hasattr(ride, 'requested_at')
    assert hasattr(ride, 'matched_at')
    assert hasattr(ride, 'pickup_time')
    assert hasattr(ride, 'start_time')
    assert hasattr(ride, 'completed_at')
    
    # Fare fields
    assert hasattr(ride, 'estimated_fare')
    assert hasattr(ride, 'final_fare')
    assert hasattr(ride, 'fare_breakdown')
    
    # Payment fields
    assert hasattr(ride, 'payment_status')
    assert hasattr(ride, 'transaction_id')
    
    # Rating fields
    assert hasattr(ride, 'rider_rating')
    assert hasattr(ride, 'rider_review')
    assert hasattr(ride, 'rider_rating_timestamp')
    assert hasattr(ride, 'driver_rating')
    assert hasattr(ride, 'driver_review')
    assert hasattr(ride, 'driver_rating_timestamp')
    
    # Cancellation fields
    assert hasattr(ride, 'cancelled_by')
    assert hasattr(ride, 'cancellation_reason')
    assert hasattr(ride, 'cancellation_fee')
    assert hasattr(ride, 'cancellation_timestamp')
