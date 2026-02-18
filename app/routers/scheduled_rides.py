"""
Scheduled Rides API endpoints.
Handles advance ride bookings up to 7 days ahead.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import uuid

from app.database import get_db
from app.models.scheduled_ride import ScheduledRide, ScheduledRideStatus
from app.models.user import User
from app.schemas.scheduled_ride import (
    ScheduledRideRequest,
    ScheduledRideUpdate,
    ScheduledRideResponse
)
from app.services.location_service import LocationService, get_location_service
from app.services.fare_service import calculate_estimated_fare
from motor.motor_asyncio import AsyncIOMotorDatabase


router = APIRouter(prefix="/api/rides/scheduled", tags=["scheduled-rides"])


@router.post("", response_model=ScheduledRideResponse, status_code=status.HTTP_201_CREATED)
async def create_scheduled_ride(
    request: ScheduledRideRequest,
    rider_id: str,
    db: Session = Depends(get_db),
    location_service: LocationService = Depends(get_location_service)
):
    """
    Create a scheduled ride for future pickup.
    
    - **pickup_location**: Pickup location with latitude, longitude, and optional address
    - **destination**: Destination location with latitude, longitude, and optional address
    - **scheduled_pickup_time**: When the ride should be picked up (ISO datetime format)
    
    Requirements: 16.1, 16.2, 16.3, 16.4
    """
    # Verify rider exists
    rider = db.query(User).filter(
        User.user_id == rider_id,
        User.user_type == "rider"
    ).first()
    
    if not rider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rider not found"
        )
    
    # Validate scheduled time is in the future
    now = datetime.utcnow()
    if request.scheduled_pickup_time <= now:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Scheduled pickup time must be in the future"
        )
    
    # Validate scheduled time is within 7 days (Requirements: 16.1)
    max_advance_time = now + timedelta(days=7)
    if request.scheduled_pickup_time > max_advance_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Scheduled pickup time cannot be more than 7 days in advance"
        )
    
    # Validate pickup location is within service area
    pickup_validation = location_service.validate_location_boundaries(
        request.pickup_location.latitude,
        request.pickup_location.longitude
    )
    
    if not pickup_validation["valid"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=pickup_validation["message"]
        )
    
    # Validate destination is within service area
    dest_validation = location_service.validate_location_boundaries(
        request.destination.latitude,
        request.destination.longitude
    )
    
    if not dest_validation["valid"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=dest_validation["message"]
        )
    
    # Calculate distance
    distance_km = location_service.calculate_distance(
        request.pickup_location.latitude,
        request.pickup_location.longitude,
        request.destination.latitude,
        request.destination.longitude
    )
    
    # Calculate estimated fare (Requirements: 16.3)
    fare_calc = calculate_estimated_fare(distance_km, surge_multiplier=1.0)
    
    # Create scheduled ride
    ride_id = f"sched_{uuid.uuid4().hex[:12]}"
    
    scheduled_ride = ScheduledRide(
        ride_id=ride_id,
        rider_id=rider_id,
        pickup_location={
            "latitude": request.pickup_location.latitude,
            "longitude": request.pickup_location.longitude,
            "address": request.pickup_location.address
        },
        destination={
            "latitude": request.destination.latitude,
            "longitude": request.destination.longitude,
            "address": request.destination.address
        },
        scheduled_pickup_time=request.scheduled_pickup_time,
        estimated_fare=fare_calc.total_fare,
        fare_breakdown={
            "base": fare_calc.base_fare,
            "per_km": fare_calc.breakdown.per_km,
            "distance": distance_km,
            "surge": fare_calc.surge_multiplier
        },
        status=ScheduledRideStatus.SCHEDULED,
        created_at=now
    )
    
    db.add(scheduled_ride)
    db.commit()
    db.refresh(scheduled_ride)
    
    return ScheduledRideResponse(
        ride_id=scheduled_ride.ride_id,
        rider_id=scheduled_ride.rider_id,
        driver_id=scheduled_ride.driver_id,
        pickup_location=scheduled_ride.pickup_location,
        destination=scheduled_ride.destination,
        scheduled_pickup_time=scheduled_ride.scheduled_pickup_time,
        estimated_fare=scheduled_ride.estimated_fare,
        fare_breakdown=scheduled_ride.fare_breakdown,
        status=scheduled_ride.status.value,
        created_at=scheduled_ride.created_at,
        modified_at=scheduled_ride.modified_at,
        matched_at=scheduled_ride.matched_at
    )


@router.get("", response_model=list[ScheduledRideResponse])
async def get_scheduled_rides(
    rider_id: str,
    status_filter: str = None,
    db: Session = Depends(get_db)
):
    """
    Get all scheduled rides for a rider.
    
    - **status_filter**: Optional filter by status (scheduled, matching, matched, etc.)
    
    Requirements: 16.12
    """
    query = db.query(ScheduledRide).filter(ScheduledRide.rider_id == rider_id)
    
    if status_filter:
        query = query.filter(ScheduledRide.status == status_filter)
    
    # Sort by scheduled pickup time
    query = query.order_by(ScheduledRide.scheduled_pickup_time)
    
    scheduled_rides = query.all()
    
    return [
        ScheduledRideResponse(
            ride_id=ride.ride_id,
            rider_id=ride.rider_id,
            driver_id=ride.driver_id,
            pickup_location=ride.pickup_location,
            destination=ride.destination,
            scheduled_pickup_time=ride.scheduled_pickup_time,
            estimated_fare=ride.estimated_fare,
            fare_breakdown=ride.fare_breakdown,
            status=ride.status.value,
            created_at=ride.created_at,
            modified_at=ride.modified_at,
            matched_at=ride.matched_at
        )
        for ride in scheduled_rides
    ]


@router.get("/{ride_id}", response_model=ScheduledRideResponse)
async def get_scheduled_ride_details(
    ride_id: str,
    db: Session = Depends(get_db)
):
    """
    Get details of a specific scheduled ride.
    """
    scheduled_ride = db.query(ScheduledRide).filter(ScheduledRide.ride_id == ride_id).first()
    
    if not scheduled_ride:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scheduled ride not found"
        )
    
    return ScheduledRideResponse(
        ride_id=scheduled_ride.ride_id,
        rider_id=scheduled_ride.rider_id,
        driver_id=scheduled_ride.driver_id,
        pickup_location=scheduled_ride.pickup_location,
        destination=scheduled_ride.destination,
        scheduled_pickup_time=scheduled_ride.scheduled_pickup_time,
        estimated_fare=scheduled_ride.estimated_fare,
        fare_breakdown=scheduled_ride.fare_breakdown,
        status=scheduled_ride.status.value,
        created_at=scheduled_ride.created_at,
        modified_at=scheduled_ride.modified_at,
        matched_at=scheduled_ride.matched_at
    )


@router.put("/{ride_id}", response_model=ScheduledRideResponse)
async def modify_scheduled_ride(
    ride_id: str,
    request: ScheduledRideUpdate,
    rider_id: str,
    db: Session = Depends(get_db),
    location_service: LocationService = Depends(get_location_service)
):
    """
    Modify a scheduled ride (pickup, destination, or scheduled time).
    
    Modifications are only allowed if the ride is at least 2 hours away.
    Fare is recalculated if locations change.
    
    Requirements: 16.6
    """
    # Get the scheduled ride
    scheduled_ride = db.query(ScheduledRide).filter(
        ScheduledRide.ride_id == ride_id,
        ScheduledRide.rider_id == rider_id
    ).first()
    
    if not scheduled_ride:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scheduled ride not found"
        )
    
    # Check if ride can be modified (must be >2 hours before pickup)
    now = datetime.utcnow()
    time_until_pickup = scheduled_ride.scheduled_pickup_time - now
    
    if time_until_pickup.total_seconds() < 7200:  # 2 hours = 7200 seconds
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot modify scheduled ride less than 2 hours before pickup time"
        )
    
    # Check if ride is in a modifiable status
    if scheduled_ride.status not in [ScheduledRideStatus.SCHEDULED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot modify ride with status: {scheduled_ride.status.value}"
        )
    
    # Track if locations changed (for fare recalculation)
    locations_changed = False
    
    # Update pickup location if provided
    if request.pickup_location:
        pickup_validation = location_service.validate_location_boundaries(
            request.pickup_location.latitude,
            request.pickup_location.longitude
        )
        
        if not pickup_validation["valid"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=pickup_validation["message"]
            )
        
        scheduled_ride.pickup_location = {
            "latitude": request.pickup_location.latitude,
            "longitude": request.pickup_location.longitude,
            "address": request.pickup_location.address
        }
        locations_changed = True
    
    # Update destination if provided
    if request.destination:
        dest_validation = location_service.validate_location_boundaries(
            request.destination.latitude,
            request.destination.longitude
        )
        
        if not dest_validation["valid"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=dest_validation["message"]
            )
        
        scheduled_ride.destination = {
            "latitude": request.destination.latitude,
            "longitude": request.destination.longitude,
            "address": request.destination.address
        }
        locations_changed = True
    
    # Update scheduled time if provided
    if request.scheduled_pickup_time:
        # Validate new time is in the future
        if request.scheduled_pickup_time <= now:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Scheduled pickup time must be in the future"
            )
        
        # Validate new time is within 7 days
        max_advance_time = now + timedelta(days=7)
        if request.scheduled_pickup_time > max_advance_time:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Scheduled pickup time cannot be more than 7 days in advance"
            )
        
        scheduled_ride.scheduled_pickup_time = request.scheduled_pickup_time
        # Reset reminder flags if time changed
        scheduled_ride.reminder_sent = False
        scheduled_ride.driver_reminder_sent = False
    
    # Recalculate fare if locations changed
    if locations_changed:
        distance_km = location_service.calculate_distance(
            scheduled_ride.pickup_location["latitude"],
            scheduled_ride.pickup_location["longitude"],
            scheduled_ride.destination["latitude"],
            scheduled_ride.destination["longitude"]
        )
        
        fare_calc = calculate_estimated_fare(distance_km, surge_multiplier=1.0)
        
        scheduled_ride.estimated_fare = fare_calc.total_fare
        scheduled_ride.fare_breakdown = {
            "base": fare_calc.base_fare,
            "per_km": fare_calc.breakdown.per_km,
            "distance": distance_km,
            "surge": fare_calc.surge_multiplier
        }
    
    # Update modified timestamp
    scheduled_ride.modified_at = now
    
    db.commit()
    db.refresh(scheduled_ride)
    
    return ScheduledRideResponse(
        ride_id=scheduled_ride.ride_id,
        rider_id=scheduled_ride.rider_id,
        driver_id=scheduled_ride.driver_id,
        pickup_location=scheduled_ride.pickup_location,
        destination=scheduled_ride.destination,
        scheduled_pickup_time=scheduled_ride.scheduled_pickup_time,
        estimated_fare=scheduled_ride.estimated_fare,
        fare_breakdown=scheduled_ride.fare_breakdown,
        status=scheduled_ride.status.value,
        created_at=scheduled_ride.created_at,
        modified_at=scheduled_ride.modified_at,
        matched_at=scheduled_ride.matched_at
    )


@router.delete("/{ride_id}")
async def cancel_scheduled_ride(
    ride_id: str,
    rider_id: str,
    db: Session = Depends(get_db)
):
    """
    Cancel a scheduled ride.
    
    Cancellation fee:
    - Free if >1 hour before pickup
    - ₹30 fee if <1 hour before pickup
    
    Requirements: 16.7, 16.8
    """
    # Get the scheduled ride
    scheduled_ride = db.query(ScheduledRide).filter(
        ScheduledRide.ride_id == ride_id,
        ScheduledRide.rider_id == rider_id
    ).first()
    
    if not scheduled_ride:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scheduled ride not found"
        )
    
    # Check if ride can be cancelled
    if scheduled_ride.status in [ScheduledRideStatus.COMPLETED, ScheduledRideStatus.CANCELLED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot cancel ride with status: {scheduled_ride.status.value}"
        )
    
    # Calculate cancellation fee based on time until pickup
    now = datetime.utcnow()
    time_until_pickup = scheduled_ride.scheduled_pickup_time - now
    
    cancellation_fee = 0.0
    if time_until_pickup.total_seconds() < 3600:  # Less than 1 hour
        cancellation_fee = 30.0
    
    # Update ride status
    scheduled_ride.status = ScheduledRideStatus.CANCELLED
    scheduled_ride.cancelled_at = now
    scheduled_ride.cancelled_by = rider_id
    scheduled_ride.cancellation_reason = "Cancelled by rider"
    scheduled_ride.cancellation_fee = cancellation_fee
    
    db.commit()
    
    return {
        "status": "success",
        "message": "Scheduled ride cancelled",
        "ride_id": ride_id,
        "cancellation_fee": cancellation_fee,
        "refund_amount": scheduled_ride.estimated_fare - cancellation_fee if cancellation_fee > 0 else scheduled_ride.estimated_fare
    }
