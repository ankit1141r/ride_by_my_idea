"""
Ride Lifecycle Management Service

This module implements ride lifecycle management functions for status transitions.
Validates Requirements: 3.3, 5.4
"""

from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import logging

from app.models.ride import Ride, RideStatus
from app.services.fare_service import calculate_final_fare

logger = logging.getLogger(__name__)


class RideLifecycleError(Exception):
    """Custom exception for ride lifecycle errors"""
    pass


def start_ride(
    ride_id: str,
    driver_id: str,
    db: Session
) -> Ride:
    """
    Start a ride by transitioning from matched/driver_arriving to in_progress.
    
    This function:
    1. Validates the ride exists and is in correct status
    2. Verifies the driver matches the assigned driver
    3. Updates status to IN_PROGRESS
    4. Records start_time
    5. Updates the ride in database
    
    Requirements: 3.3
    
    Args:
        ride_id: Unique ride identifier
        driver_id: ID of the driver starting the ride
        db: Database session
    
    Returns:
        Updated Ride object with IN_PROGRESS status
    
    Raises:
        HTTPException 404: If ride not found
        HTTPException 403: If driver doesn't match assigned driver
        HTTPException 422: If ride status doesn't allow starting
    """
    logger.info(f"Starting ride | ride_id={ride_id} | driver_id={driver_id}")
    
    # Fetch the ride
    ride = db.query(Ride).filter(Ride.ride_id == ride_id).first()
    
    if not ride:
        logger.warning(f"Ride not found | ride_id={ride_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ride {ride_id} not found"
        )
    
    # Verify driver matches
    if ride.driver_id != driver_id:
        logger.warning(
            f"Driver mismatch | ride_id={ride_id} | "
            f"expected={ride.driver_id} | actual={driver_id}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Driver ID does not match assigned driver for this ride"
        )
    
    # Check if ride can transition to IN_PROGRESS
    # Valid statuses: MATCHED or DRIVER_ARRIVING
    if ride.status not in [RideStatus.MATCHED, RideStatus.DRIVER_ARRIVING]:
        logger.warning(
            f"Invalid status for start | ride_id={ride_id} | status={ride.status.value}"
        )
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Cannot start ride with status {ride.status.value}. "
                   f"Ride must be in matched or driver_arriving status."
        )
    
    # Update ride status and start time
    ride.status = RideStatus.IN_PROGRESS
    ride.start_time = datetime.utcnow()
    
    # If pickup_time wasn't set yet, set it now
    if not ride.pickup_time:
        ride.pickup_time = datetime.utcnow()
    
    db.commit()
    db.refresh(ride)
    
    logger.info(f"Ride started successfully | ride_id={ride_id} | rider_id={ride.rider_id}")
    
    return ride


def complete_ride(
    ride_id: str,
    driver_id: str,
    actual_distance_km: float,
    db: Session,
    actual_route: Optional[list] = None
) -> Ride:
    """
    Complete a ride by transitioning from in_progress to completed.
    
    This function:
    1. Validates the ride exists and is in progress
    2. Verifies the driver matches the assigned driver
    3. Calculates final fare based on actual distance with fare protection
    4. Updates status to COMPLETED
    5. Records completed_at timestamp
    6. Stores actual route if provided
    7. Updates the ride in database
    
    Requirements: 3.3, 5.4
    
    Args:
        ride_id: Unique ride identifier
        driver_id: ID of the driver completing the ride
        actual_distance_km: Actual distance traveled in kilometers
        db: Database session
        actual_route: Optional list of location points taken during ride
    
    Returns:
        Updated Ride object with COMPLETED status and final fare
    
    Raises:
        HTTPException 404: If ride not found
        HTTPException 403: If driver doesn't match assigned driver
        HTTPException 422: If ride status doesn't allow completion
        HTTPException 400: If actual_distance_km is invalid
    """
    # Validate actual distance
    if actual_distance_km < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Actual distance must be non-negative"
        )
    
    # Fetch the ride
    ride = db.query(Ride).filter(Ride.ride_id == ride_id).first()
    
    if not ride:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ride {ride_id} not found"
        )
    
    # Verify driver matches
    if ride.driver_id != driver_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Driver ID does not match assigned driver for this ride"
        )
    
    # Check if ride can transition to COMPLETED
    if not ride.can_transition_to(RideStatus.COMPLETED):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Cannot complete ride with status {ride.status.value}. "
                   f"Ride must be in in_progress status."
        )
    
    # Get surge multiplier from fare breakdown
    surge_multiplier = ride.fare_breakdown.get("surge", 1.0)
    
    # Calculate final fare with fare protection (Requirement 5.4, 5.5)
    final_fare_calculation = calculate_final_fare(
        actual_distance_km=actual_distance_km,
        estimated_fare=ride.estimated_fare,
        surge_multiplier=surge_multiplier
    )
    
    # Update ride with completion details
    ride.status = RideStatus.COMPLETED
    ride.completed_at = datetime.utcnow()
    ride.final_fare = final_fare_calculation.total_fare
    
    # Update fare breakdown with actual distance - need to create a new dict to trigger SQLAlchemy update
    updated_breakdown = ride.fare_breakdown.copy()
    updated_breakdown["distance"] = actual_distance_km
    updated_breakdown["final_total"] = final_fare_calculation.total_fare
    ride.fare_breakdown = updated_breakdown
    
    # Store actual route if provided
    if actual_route:
        ride.actual_route = actual_route
    
    db.commit()
    db.refresh(ride)
    
    return ride


def cancel_ride(
    ride_id: str,
    user_id: str,
    cancellation_reason: Optional[str],
    db: Session
) -> Ride:
    """
    Cancel a ride based on current status and user role.
    
    This function:
    1. Validates the ride exists and can be cancelled
    2. Determines cancellation fee based on ride status
    3. Updates ride status to CANCELLED
    4. Records cancellation details (who cancelled, reason, fee, timestamp)
    
    Cancellation Rules (Requirements 15.1, 15.2, 15.3, 15.7):
    - Pre-match (REQUESTED): No fee, anyone can cancel
    - Post-match (MATCHED, DRIVER_ARRIVING): ₹20 fee for rider, no fee for driver
    - In-progress: Cannot cancel
    - Already completed/cancelled: Cannot cancel
    
    Requirements: 15.1, 15.2, 15.3, 15.7
    
    Args:
        ride_id: Unique ride identifier
        user_id: ID of the user cancelling (rider or driver)
        cancellation_reason: Optional reason for cancellation
        db: Database session
    
    Returns:
        Updated Ride object with CANCELLED status
    
    Raises:
        HTTPException 404: If ride not found
        HTTPException 403: If user not authorized to cancel this ride
        HTTPException 422: If ride status doesn't allow cancellation
    """
    # Fetch the ride
    ride = db.query(Ride).filter(Ride.ride_id == ride_id).first()
    
    if not ride:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ride {ride_id} not found"
        )
    
    # Verify user is authorized (must be rider or driver of this ride)
    if ride.rider_id != user_id and ride.driver_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to cancel this ride"
        )
    
    # Check if ride can be cancelled (Requirement 15.7)
    if not ride.is_cancellable():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Cannot cancel ride with status {ride.status.value}. "
                   f"Cancellation is only allowed before ride starts."
        )
    
    # Determine cancellation fee based on status and who is cancelling
    cancellation_fee = 0.0
    
    # Requirement 15.1: Pre-match cancellation - no fee
    if ride.status == RideStatus.REQUESTED:
        cancellation_fee = 0.0
    
    # Requirement 15.2: Post-match cancellation by rider - ₹20 fee
    elif ride.status in [RideStatus.MATCHED, RideStatus.DRIVER_ARRIVING]:
        if user_id == ride.rider_id:
            cancellation_fee = 20.0
        else:
            # Driver cancellation - no fee (Requirement 15.3)
            cancellation_fee = 0.0
    
    # Update ride with cancellation details
    ride.status = RideStatus.CANCELLED
    ride.cancelled_by = user_id
    ride.cancellation_reason = cancellation_reason
    ride.cancellation_fee = cancellation_fee
    ride.cancellation_timestamp = datetime.utcnow()
    
    db.commit()
    db.refresh(ride)
    
    return ride


def get_ride_status(ride_id: str, db: Session) -> Dict[str, Any]:
    """
    Get current status and details of a ride.
    
    Args:
        ride_id: Unique ride identifier
        db: Database session
    
    Returns:
        Dictionary with ride status and relevant details
    
    Raises:
        HTTPException 404: If ride not found
    """
    ride = db.query(Ride).filter(Ride.ride_id == ride_id).first()
    
    if not ride:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ride {ride_id} not found"
        )
    
    return {
        "ride_id": ride.ride_id,
        "status": ride.status.value,
        "rider_id": ride.rider_id,
        "driver_id": ride.driver_id,
        "pickup_location": ride.pickup_location,
        "destination": ride.destination,
        "requested_at": ride.requested_at,
        "matched_at": ride.matched_at,
        "pickup_time": ride.pickup_time,
        "start_time": ride.start_time,
        "completed_at": ride.completed_at,
        "estimated_fare": ride.estimated_fare,
        "final_fare": ride.final_fare,
        "payment_status": ride.payment_status.value
    }
