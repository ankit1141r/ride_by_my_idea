"""
Location API endpoints for driver location tracking.
Handles real-time location updates and queries.

Requirements: 4.4, 8.1, 8.2
"""
from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Optional

from app.database import get_mongodb
from app.services.location_service import LocationService
from app.schemas.location import (
    DriverLocationUpdate,
    DriverLocationResponse,
    LocationValidationResponse
)
from app.utils.jwt import get_current_user_dependency as get_current_user

router = APIRouter(
    prefix="/api/location",
    tags=["location"]
)


@router.post(
    "/driver",
    response_model=DriverLocationResponse,
    status_code=status.HTTP_200_OK,
    summary="Update driver location",
    description="Update driver's current location. Requires driver authentication."
)
async def update_driver_location(
    location_data: DriverLocationUpdate,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_mongodb)
):
    """
    Update driver's current location in MongoDB.
    
    This endpoint is called by drivers to update their real-time location.
    Location updates should occur every 10 seconds while driver is available or on a ride.
    
    Args:
        location_data: Location update data (latitude, longitude, etc.)
        current_user: Authenticated user from JWT token
        db: MongoDB database instance
        
    Returns:
        DriverLocationResponse with updated location details
        
    Raises:
        HTTPException 403: If user is not a driver
        HTTPException 400: If location is outside service area
        
    Requirements: 4.4, 8.1, 8.2
    """
    # Verify user is a driver
    if current_user.get("user_type") != "driver":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only drivers can update location"
        )
    
    driver_id = current_user["user_id"]
    location_service = LocationService(db)
    
    # Validate location is within service area
    validation = location_service.validate_location_boundaries(
        location_data.latitude,
        location_data.longitude
    )
    
    if not validation["valid"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=validation["message"]
        )
    
    # Update driver location
    location = await location_service.update_driver_location(
        driver_id=driver_id,
        latitude=location_data.latitude,
        longitude=location_data.longitude,
        address=location_data.address,
        status=location_data.status,
        accuracy=location_data.accuracy
    )
    
    return DriverLocationResponse(
        user_id=location.user_id,
        latitude=location.get_latitude(),
        longitude=location.get_longitude(),
        address=location.address,
        status=location.status,
        accuracy=location.accuracy,
        timestamp=location.timestamp,
        message="Location updated successfully"
    )


@router.get(
    "/driver/{driver_id}",
    response_model=DriverLocationResponse,
    status_code=status.HTTP_200_OK,
    summary="Get driver location",
    description="Get the most recent location for a driver."
)
async def get_driver_location(
    driver_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_mongodb)
):
    """
    Get the most recent location for a driver.
    
    This endpoint is used by riders to track their matched driver's location
    in real-time during ride matching and active rides.
    
    Args:
        driver_id: Driver's user ID
        current_user: Authenticated user from JWT token
        db: MongoDB database instance
        
    Returns:
        DriverLocationResponse with driver's current location
        
    Raises:
        HTTPException 404: If driver location not found
        
    Requirements: 8.1
    """
    location_service = LocationService(db)
    
    # Get driver location
    location = await location_service.get_driver_location(driver_id)
    
    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Location not found for driver {driver_id}"
        )
    
    return DriverLocationResponse(
        user_id=location.user_id,
        latitude=location.get_latitude(),
        longitude=location.get_longitude(),
        address=location.address,
        status=location.status,
        accuracy=location.accuracy,
        timestamp=location.timestamp,
        message="Location retrieved successfully"
    )


@router.post(
    "/validate",
    response_model=LocationValidationResponse,
    status_code=status.HTTP_200_OK,
    summary="Validate location boundaries",
    description="Check if a location is within the Indore service area."
)
async def validate_location(
    latitude: float,
    longitude: float,
    db: AsyncIOMotorDatabase = Depends(get_mongodb)
):
    """
    Validate if a location is within service boundaries.
    
    This endpoint can be used by clients to validate pickup and destination
    locations before creating ride requests.
    
    Args:
        latitude: Latitude coordinate
        longitude: Longitude coordinate
        db: MongoDB database instance
        
    Returns:
        LocationValidationResponse with validation result
        
    Requirements: 2.4, 13.6
    """
    location_service = LocationService(db)
    
    validation = location_service.validate_location_boundaries(latitude, longitude)
    
    return LocationValidationResponse(
        valid=validation["valid"],
        message=validation["message"],
        latitude=validation["latitude"],
        longitude=validation["longitude"]
    )
