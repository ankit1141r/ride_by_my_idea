"""
Ride management API endpoints.

This module implements ride request creation and management endpoints.
Requirements: 2.1, 2.2, 2.4, 2.5
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime
from typing import Optional
import uuid

from app.database import get_db, get_mongodb
from app.schemas.ride import (
    RideRequestCreate,
    RideRequestResponse,
    FareBreakdownResponse,
    RideHistoryResponse,
    RideHistoryItem,
    RideDetailsResponse,
    ErrorResponse
)
from app.models.ride import Ride, RideStatus, PaymentStatus
from app.services.location_service import LocationService
from app.services.fare_service import calculate_estimated_fare
from app.services.ride_service import start_ride, complete_ride, get_ride_status, cancel_ride
from app.utils.jwt import get_current_user_dependency

router = APIRouter(
    prefix="/api/rides",
    tags=["rides"]
)


@router.post(
    "/request",
    response_model=RideRequestResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid request data"},
        422: {"model": ErrorResponse, "description": "Location outside service area"}
    }
)
async def create_ride_request(
    ride_request: RideRequestCreate,
    db: Session = Depends(get_db),
    mongodb: AsyncIOMotorDatabase = Depends(get_mongodb),
    current_user: dict = Depends(get_current_user_dependency)
):
    """
    Create a new ride request.
    
    This endpoint:
    1. Validates pickup and destination are within Indore boundaries
    2. Calculates estimated fare based on distance
    3. Creates a RideRequest record in the database
    4. Returns request ID and fare details
    
    Requirements: 2.1, 2.2, 2.4, 2.5
    
    Args:
        ride_request: Ride request data with pickup and destination
        db: PostgreSQL database session
        mongodb: MongoDB database instance
        current_user: Authenticated user from JWT token
    
    Returns:
        RideRequestResponse with request ID, fare details, and estimated arrival
    
    Raises:
        HTTPException 422: If pickup or destination is outside service area
        HTTPException 400: If request data is invalid
    """
    # Verify user is a rider
    if current_user.get("user_type") != "rider":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only riders can create ride requests"
        )
    
    rider_id = current_user.get("user_id")
    
    # Initialize location service
    location_service = LocationService(mongodb)
    
    # Validate pickup location is within service area (Requirement 2.4)
    pickup_validation = location_service.validate_location_boundaries(
        ride_request.pickup_location.latitude,
        ride_request.pickup_location.longitude
    )
    
    if not pickup_validation["valid"]:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "error": "boundary_violation",
                "message": pickup_validation["message"],
                "details": {
                    "location_type": "pickup",
                    "latitude": ride_request.pickup_location.latitude,
                    "longitude": ride_request.pickup_location.longitude
                }
            }
        )
    
    # Validate destination is within service area (Requirement 2.4)
    destination_validation = location_service.validate_location_boundaries(
        ride_request.destination.latitude,
        ride_request.destination.longitude
    )
    
    if not destination_validation["valid"]:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "error": "boundary_violation",
                "message": destination_validation["message"],
                "details": {
                    "location_type": "destination",
                    "latitude": ride_request.destination.latitude,
                    "longitude": ride_request.destination.longitude
                }
            }
        )
    
    # Calculate distance between pickup and destination (Requirement 2.2)
    distance_km = location_service.calculate_distance(
        ride_request.pickup_location.latitude,
        ride_request.pickup_location.longitude,
        ride_request.destination.latitude,
        ride_request.destination.longitude
    )
    
    # Calculate estimated fare (Requirement 2.2, 5.1, 5.2)
    # Using default surge multiplier of 1.0 for now
    fare_calculation = calculate_estimated_fare(
        distance_km=distance_km,
        surge_multiplier=1.0
    )
    
    # Generate unique ride ID
    ride_id = f"ride_{uuid.uuid4().hex[:12]}"
    
    # Create pickup and destination location dictionaries
    pickup_location_dict = {
        "latitude": ride_request.pickup_location.latitude,
        "longitude": ride_request.pickup_location.longitude,
        "address": ride_request.pickup_location.address
    }
    
    destination_dict = {
        "latitude": ride_request.destination.latitude,
        "longitude": ride_request.destination.longitude,
        "address": ride_request.destination.address
    }
    
    # Create fare breakdown dictionary
    fare_breakdown_dict = {
        "base": fare_calculation.base_fare,
        "per_km": fare_calculation.breakdown.per_km,
        "distance": distance_km,
        "surge": fare_calculation.surge_multiplier,
        "total": fare_calculation.total_fare
    }
    
    # Create Ride record in database (Requirement 2.1)
    ride = Ride(
        ride_id=ride_id,
        rider_id=rider_id,
        status=RideStatus.REQUESTED,
        pickup_location=pickup_location_dict,
        destination=destination_dict,
        requested_at=datetime.utcnow(),
        estimated_fare=fare_calculation.total_fare,
        fare_breakdown=fare_breakdown_dict,
        payment_status=PaymentStatus.PENDING
    )
    
    db.add(ride)
    db.commit()
    db.refresh(ride)
    
    # Estimate arrival time (Requirement 2.5)
    # For now, using a simple heuristic: 10 minutes base + 2 minutes per km
    # In production, this would use real-time driver availability and traffic data
    estimated_arrival_minutes = 10 + int(distance_km * 2)
    
    # Prepare response
    response = RideRequestResponse(
        request_id=ride_id,
        estimated_fare=fare_calculation.total_fare,
        estimated_arrival=estimated_arrival_minutes,
        fare_breakdown=FareBreakdownResponse(
            base=fare_calculation.base_fare,
            per_km=fare_calculation.breakdown.per_km,
            distance=distance_km,
            surge=fare_calculation.surge_multiplier
        ),
        pickup_location=pickup_location_dict,
        destination=destination_dict,
        requested_at=ride.requested_at,
        status=ride.status.value,
        message="Ride request created successfully"
    )
    
    return response



@router.post(
    "/{ride_id}/start",
    status_code=status.HTTP_200_OK,
    responses={
        404: {"description": "Ride not found"},
        403: {"description": "Driver not authorized"},
        422: {"description": "Invalid ride status for starting"}
    }
)
async def start_ride_endpoint(
    ride_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user_dependency)
):
    """
    Start a ride (transition to in_progress status).
    
    This endpoint:
    1. Validates the driver is authorized for this ride
    2. Transitions ride status from matched/driver_arriving to in_progress
    3. Records the start time
    
    Requirements: 3.3
    
    Args:
        ride_id: Unique ride identifier
        db: PostgreSQL database session
        current_user: Authenticated user from JWT token
    
    Returns:
        Updated ride details with in_progress status
    
    Raises:
        HTTPException 403: If user is not a driver or not assigned to this ride
        HTTPException 404: If ride not found
        HTTPException 422: If ride status doesn't allow starting
    """
    # Verify user is a driver
    if current_user.get("user_type") != "driver":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only drivers can start rides"
        )
    
    driver_id = current_user.get("user_id")
    
    # Start the ride
    ride = start_ride(ride_id=ride_id, driver_id=driver_id, db=db)
    
    return {
        "ride_id": ride.ride_id,
        "status": ride.status.value,
        "start_time": ride.start_time,
        "pickup_time": ride.pickup_time,
        "message": "Ride started successfully"
    }


@router.post(
    "/{ride_id}/complete",
    status_code=status.HTTP_200_OK,
    responses={
        404: {"description": "Ride not found"},
        403: {"description": "Driver not authorized"},
        422: {"description": "Invalid ride status for completion"},
        400: {"description": "Invalid actual distance"}
    }
)
async def complete_ride_endpoint(
    ride_id: str,
    actual_distance_km: float,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user_dependency)
):
    """
    Complete a ride (transition to completed status with final fare).
    
    This endpoint:
    1. Validates the driver is authorized for this ride
    2. Calculates final fare based on actual distance with fare protection
    3. Transitions ride status from in_progress to completed
    4. Records the completion time
    
    Requirements: 3.3, 5.4
    
    Args:
        ride_id: Unique ride identifier
        actual_distance_km: Actual distance traveled in kilometers
        db: PostgreSQL database session
        current_user: Authenticated user from JWT token
    
    Returns:
        Updated ride details with completed status and final fare
    
    Raises:
        HTTPException 403: If user is not a driver or not assigned to this ride
        HTTPException 404: If ride not found
        HTTPException 422: If ride status doesn't allow completion
        HTTPException 400: If actual_distance_km is invalid
    """
    # Verify user is a driver
    if current_user.get("user_type") != "driver":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only drivers can complete rides"
        )
    
    driver_id = current_user.get("user_id")
    
    # Complete the ride
    ride = complete_ride(
        ride_id=ride_id,
        driver_id=driver_id,
        actual_distance_km=actual_distance_km,
        db=db
    )
    
    return {
        "ride_id": ride.ride_id,
        "status": ride.status.value,
        "completed_at": ride.completed_at,
        "estimated_fare": ride.estimated_fare,
        "final_fare": ride.final_fare,
        "fare_breakdown": ride.fare_breakdown,
        "message": "Ride completed successfully"
    }


@router.post(
    "/{ride_id}/cancel",
    status_code=status.HTTP_200_OK,
    responses={
        404: {"description": "Ride not found"},
        403: {"description": "User not authorized to cancel this ride"},
        422: {"description": "Ride cannot be cancelled in current status"}
    }
)
async def cancel_ride_endpoint(
    ride_id: str,
    cancellation_reason: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user_dependency)
):
    """
    Cancel a ride based on current status.
    
    This endpoint:
    1. Validates user is authorized (rider or driver of the ride)
    2. Checks if ride status allows cancellation
    3. Calculates cancellation fee based on status and who is cancelling
    4. Updates ride status to cancelled
    5. Records cancellation details
    
    Cancellation Rules:
    - Pre-match (REQUESTED): No fee
    - Post-match (MATCHED, DRIVER_ARRIVING): ₹20 fee for rider, no fee for driver
    - In-progress: Cannot cancel
    
    Requirements: 15.1, 15.2, 15.3, 15.7
    
    Args:
        ride_id: Unique ride identifier
        cancellation_reason: Optional reason for cancellation
        db: PostgreSQL database session
        current_user: Authenticated user from JWT token
    
    Returns:
        Updated ride details with cancelled status and cancellation fee
    
    Raises:
        HTTPException 403: If user not authorized to cancel this ride
        HTTPException 404: If ride not found
        HTTPException 422: If ride status doesn't allow cancellation
    """
    user_id = current_user.get("user_id")
    
    # Cancel the ride
    ride = cancel_ride(
        ride_id=ride_id,
        user_id=user_id,
        cancellation_reason=cancellation_reason,
        db=db
    )
    
    return {
        "ride_id": ride.ride_id,
        "status": ride.status.value,
        "cancelled_by": ride.cancelled_by,
        "cancellation_reason": ride.cancellation_reason,
        "cancellation_fee": ride.cancellation_fee,
        "cancellation_timestamp": ride.cancellation_timestamp,
        "message": f"Ride cancelled successfully. Cancellation fee: ₹{ride.cancellation_fee}"
    }


@router.get(
    "/{ride_id}/status",
    status_code=status.HTTP_200_OK,
    responses={
        404: {"description": "Ride not found"}
    }
)
async def get_ride_status_endpoint(
    ride_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user_dependency)
):
    """
    Get current status and details of a ride.
    
    Requirements: 3.3
    
    Args:
        ride_id: Unique ride identifier
        db: PostgreSQL database session
        current_user: Authenticated user from JWT token
    
    Returns:
        Ride status and details
    
    Raises:
        HTTPException 404: If ride not found
    """
    ride_status = get_ride_status(ride_id=ride_id, db=db)
    
    # Verify user is authorized to view this ride (rider or driver)
    user_id = current_user.get("user_id")
    if ride_status["rider_id"] != user_id and ride_status["driver_id"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this ride"
        )
    
    return ride_status



@router.get(
    "/history",
    response_model=RideHistoryResponse,
    status_code=status.HTTP_200_OK,
    responses={
        401: {"description": "Unauthorized"}
    }
)
async def get_ride_history(
    start_date: Optional[datetime] = Query(None, description="Filter rides from this date (inclusive)"),
    end_date: Optional[datetime] = Query(None, description="Filter rides until this date (inclusive)"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user_dependency)
):
    """
    Get ride history for the authenticated user.
    
    This endpoint:
    1. Returns all rides for the user (as rider or driver)
    2. Sorts rides in reverse chronological order (most recent first)
    3. Supports filtering by date range
    4. Returns rides with all required fields
    
    Requirements: 9.1, 9.2, 9.3, 9.4
    
    Args:
        start_date: Optional start date for filtering (inclusive)
        end_date: Optional end date for filtering (inclusive)
        db: PostgreSQL database session
        current_user: Authenticated user from JWT token
    
    Returns:
        RideHistoryResponse with list of rides in reverse chronological order
    """
    user_id = current_user.get("user_id")
    user_type = current_user.get("user_type")
    
    # Build query based on user type
    query = db.query(Ride)
    
    if user_type == "rider":
        query = query.filter(Ride.rider_id == user_id)
    elif user_type == "driver":
        query = query.filter(Ride.driver_id == user_id)
    else:
        # If user type is unknown, show rides where they are either rider or driver
        query = query.filter((Ride.rider_id == user_id) | (Ride.driver_id == user_id))
    
    # Apply date range filters (Requirement 9.4)
    if start_date:
        query = query.filter(Ride.requested_at >= start_date)
    
    if end_date:
        query = query.filter(Ride.requested_at <= end_date)
    
    # Sort in reverse chronological order (Requirement 9.2)
    query = query.order_by(Ride.requested_at.desc())
    
    # Execute query
    rides = query.all()
    
    # Build response with required fields (Requirement 9.3)
    ride_items = []
    for ride in rides:
        # Determine which rating to show based on user type
        if user_type == "rider":
            # Rider sees the rating they gave to the driver
            rating = ride.driver_rating
        else:
            # Driver sees the rating they gave to the rider
            rating = ride.rider_rating
        
        # Use completed_at if available, otherwise use requested_at
        ride_date = ride.completed_at if ride.completed_at else ride.requested_at
        
        # Use final_fare if available, otherwise use estimated_fare
        fare = ride.final_fare if ride.final_fare is not None else ride.estimated_fare
        
        ride_item = RideHistoryItem(
            ride_id=ride.ride_id,
            date=ride_date,
            pickup_location=ride.pickup_location,
            destination=ride.destination,
            fare=fare,
            status=ride.status.value,
            driver_rating=ride.driver_rating if user_type == "rider" else None,
            rider_rating=ride.rider_rating if user_type == "driver" else None
        )
        ride_items.append(ride_item)
    
    return RideHistoryResponse(
        rides=ride_items,
        total=len(ride_items)
    )


@router.get(
    "/{ride_id}",
    response_model=RideDetailsResponse,
    status_code=status.HTTP_200_OK,
    responses={
        404: {"description": "Ride not found"},
        403: {"description": "Not authorized to view this ride"}
    }
)
async def get_ride_details(
    ride_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user_dependency)
):
    """
    Get detailed view of a specific ride.
    
    This endpoint:
    1. Returns complete ride details including route map and payment receipt
    2. Verifies user is authorized to view the ride (rider or driver)
    3. Includes all timing, fare, payment, and rating information
    
    Requirements: 9.3, 9.5
    
    Args:
        ride_id: Unique ride identifier
        db: PostgreSQL database session
        current_user: Authenticated user from JWT token
    
    Returns:
        RideDetailsResponse with complete ride information
    
    Raises:
        HTTPException 404: If ride not found
        HTTPException 403: If user not authorized to view this ride
    """
    user_id = current_user.get("user_id")
    
    # Query ride
    ride = db.query(Ride).filter(Ride.ride_id == ride_id).first()
    
    if not ride:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ride not found"
        )
    
    # Verify user is authorized (rider or driver of this ride)
    if ride.rider_id != user_id and ride.driver_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this ride"
        )
    
    # Build detailed response (Requirement 9.5)
    response = RideDetailsResponse(
        ride_id=ride.ride_id,
        rider_id=ride.rider_id,
        driver_id=ride.driver_id,
        status=ride.status.value,
        pickup_location=ride.pickup_location,
        destination=ride.destination,
        actual_route=ride.actual_route,
        requested_at=ride.requested_at,
        matched_at=ride.matched_at,
        pickup_time=ride.pickup_time,
        start_time=ride.start_time,
        completed_at=ride.completed_at,
        estimated_fare=ride.estimated_fare,
        final_fare=ride.final_fare,
        fare_breakdown=ride.fare_breakdown,
        payment_status=ride.payment_status.value,
        transaction_id=ride.transaction_id,
        rider_rating=ride.rider_rating,
        rider_review=ride.rider_review,
        driver_rating=ride.driver_rating,
        driver_review=ride.driver_review,
        cancelled_by=ride.cancelled_by,
        cancellation_reason=ride.cancellation_reason,
        cancellation_fee=ride.cancellation_fee
    )
    
    return response



@router.get("/{ride_id}/route")
async def get_ride_route(
    ride_id: str,
    current_user: dict = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """
    Get current route for an in-progress ride.
    Returns route polyline and estimated time to destination.
    
    - **ride_id**: Ride identifier
    """
    import json
    from app.database import get_mongodb
    from app.services.location_service import LocationService
    
    # Get ride
    ride = db.query(Ride).filter(Ride.ride_id == ride_id).first()
    if not ride:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ride not found"
        )
    
    # Verify user is part of the ride
    if current_user["user_id"] not in [ride.rider_id, ride.driver_id]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to view this ride's route"
        )
    
    # Verify ride is in progress
    if ride.status != RideStatus.IN_PROGRESS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Route is only available for in-progress rides"
        )
    
    # Get current driver location
    mongodb = get_mongodb()
    location_service = LocationService(db, mongodb)
    
    try:
        driver_location = location_service.get_driver_location(ride.driver_id)
        if not driver_location:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Driver location not available"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get driver location: {str(e)}"
        )
    
    # Parse destination
    destination = json.loads(ride.destination)
    
    # Get route from current location to destination
    try:
        route = location_service.get_route(
            driver_location["latitude"],
            driver_location["longitude"],
            destination["latitude"],
            destination["longitude"]
        )
        
        return {
            "ride_id": ride_id,
            "status": ride.status.value,
            "current_location": {
                "latitude": driver_location["latitude"],
                "longitude": driver_location["longitude"]
            },
            "destination": destination,
            "route": {
                "distance_km": route["distance"],
                "duration_minutes": route["duration"],
                "polyline": route["polyline"]
            },
            "estimated_time_to_destination": route["duration"]
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate route: {str(e)}"
        )


@router.get("/{ride_id}/receipt")
async def get_ride_receipt(
    ride_id: str,
    current_user: dict = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """
    Generate and download PDF receipt for a completed ride.
    
    - **ride_id**: Ride identifier
    """
    from io import BytesIO
    from fastapi.responses import StreamingResponse
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    from reportlab.lib.units import inch
    import json
    from datetime import datetime
    
    # Get ride
    ride = db.query(Ride).filter(Ride.ride_id == ride_id).first()
    if not ride:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ride not found"
        )
    
    # Verify user is part of the ride
    if current_user["user_id"] not in [ride.rider_id, ride.driver_id]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to view this ride's receipt"
        )
    
    # Verify ride is completed
    if ride.status != RideStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Receipt is only available for completed rides"
        )
    
    # Get rider and driver info
    rider = db.query(User).filter(User.user_id == ride.rider_id).first()
    driver = db.query(User).filter(User.user_id == ride.driver_id).first()
    
    # Parse locations
    pickup = json.loads(ride.pickup_location)
    destination = json.loads(ride.destination)
    
    # Create PDF
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # Title
    p.setFont("Helvetica-Bold", 20)
    p.drawString(1 * inch, height - 1 * inch, "Ride Receipt")
    
    # Ride details
    p.setFont("Helvetica", 12)
    y = height - 1.5 * inch
    
    p.drawString(1 * inch, y, f"Ride ID: {ride_id}")
    y -= 0.3 * inch
    
    p.drawString(1 * inch, y, f"Date: {ride.completed_at.strftime('%Y-%m-%d %H:%M:%S')}")
    y -= 0.3 * inch
    
    p.drawString(1 * inch, y, f"Rider: {rider.name}")
    y -= 0.3 * inch
    
    p.drawString(1 * inch, y, f"Driver: {driver.name}")
    y -= 0.5 * inch
    
    # Locations
    p.setFont("Helvetica-Bold", 14)
    p.drawString(1 * inch, y, "Trip Details")
    y -= 0.3 * inch
    
    p.setFont("Helvetica", 12)
    p.drawString(1 * inch, y, f"Pickup: {pickup.get('address', 'N/A')}")
    y -= 0.3 * inch
    
    p.drawString(1 * inch, y, f"Destination: {destination.get('address', 'N/A')}")
    y -= 0.5 * inch
    
    # Fare breakdown
    p.setFont("Helvetica-Bold", 14)
    p.drawString(1 * inch, y, "Fare Breakdown")
    y -= 0.3 * inch
    
    p.setFont("Helvetica", 12)
    fare_breakdown = json.loads(ride.fare_breakdown)
    
    p.drawString(1 * inch, y, f"Base Fare: ₹{fare_breakdown.get('base_fare', 0):.2f}")
    y -= 0.3 * inch
    
    p.drawString(1 * inch, y, f"Distance ({fare_breakdown.get('distance', 0):.2f} km): ₹{fare_breakdown.get('distance_charge', 0):.2f}")
    y -= 0.3 * inch
    
    if fare_breakdown.get('surge_multiplier', 1.0) > 1.0:
        p.drawString(1 * inch, y, f"Surge Multiplier: {fare_breakdown.get('surge_multiplier', 1.0)}x")
        y -= 0.3 * inch
    
    # Total
    p.setFont("Helvetica-Bold", 14)
    p.drawString(1 * inch, y, f"Total Fare: ₹{ride.final_fare:.2f}")
    y -= 0.5 * inch
    
    # Payment info
    if ride.payment_status == "completed":
        p.setFont("Helvetica", 12)
        p.drawString(1 * inch, y, f"Payment Status: Paid")
        y -= 0.3 * inch
        
        if ride.transaction_id:
            p.drawString(1 * inch, y, f"Transaction ID: {ride.transaction_id}")
    
    # Footer
    p.setFont("Helvetica", 10)
    p.drawString(1 * inch, 1 * inch, "Thank you for using our service!")
    
    p.showPage()
    p.save()
    
    buffer.seek(0)
    
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=ride_receipt_{ride_id}.pdf"
        }
    )
