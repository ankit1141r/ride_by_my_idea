"""
Driver-related API endpoints.
Handles driver availability, status management, and driver-specific operations.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional
from app.database import get_db, get_redis
from app.services.matching_service import MatchingService
from app.models.user import User
from redis import Redis


router = APIRouter(prefix="/api/drivers", tags=["drivers"])


class DriverAvailabilityRequest(BaseModel):
    """Request to set driver availability status."""
    status: str = Field(..., description="Driver status: 'available' or 'unavailable'")
    latitude: Optional[float] = Field(None, description="Current latitude (required when setting available)")
    longitude: Optional[float] = Field(None, description="Current longitude (required when setting available)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "available",
                "latitude": 22.7196,
                "longitude": 75.8577
            }
        }


class DriverAvailabilityResponse(BaseModel):
    """Response for driver availability operations."""
    status: str
    message: str
    location: Optional[dict] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "message": "Driver is now available",
                "location": {
                    "latitude": 22.7196,
                    "longitude": 75.8577
                }
            }
        }


class DriverStatusResponse(BaseModel):
    """Response for driver status query."""
    driver_id: str
    status: str
    timestamp: str
    location: Optional[dict] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "driver_id": "driver123",
                "status": "available",
                "timestamp": "2024-01-15T10:30:00",
                "location": {
                    "latitude": 22.7196,
                    "longitude": 75.8577
                }
            }
        }


@router.post("/availability", response_model=DriverAvailabilityResponse)
async def set_driver_availability(
    request: DriverAvailabilityRequest,
    driver_id: str,
    db: Session = Depends(get_db),
    redis_client: Redis = Depends(get_redis)
):
    """
    Set driver availability status.
    
    - **status**: 'available' or 'unavailable'
    - **latitude**: Required when setting status to 'available'
    - **longitude**: Required when setting status to 'available'
    """
    # Verify driver exists
    driver = db.query(User).filter(
        User.user_id == driver_id,
        User.user_type == "driver"
    ).first()
    
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Driver not found"
        )
    
    matching_service = MatchingService(redis_client, db)
    
    try:
        if request.status == "available":
            # Validate location is provided
            if request.latitude is None or request.longitude is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Latitude and longitude are required when setting status to available"
                )
            
            result = matching_service.set_driver_available(
                driver_id,
                request.latitude,
                request.longitude
            )
        elif request.status == "unavailable":
            result = matching_service.set_driver_unavailable(driver_id)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid status. Must be 'available' or 'unavailable'"
            )
        
        return DriverAvailabilityResponse(**result)
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update driver availability: {str(e)}"
        )


@router.get("/availability/{driver_id}", response_model=DriverStatusResponse)
async def get_driver_availability(
    driver_id: str,
    redis_client: Redis = Depends(get_redis),
    db: Session = Depends(get_db)
):
    """
    Get driver's current availability status.
    
    - **driver_id**: Driver's user ID
    """
    # Verify driver exists
    driver = db.query(User).filter(
        User.user_id == driver_id,
        User.user_type == "driver"
    ).first()
    
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Driver not found"
        )
    
    matching_service = MatchingService(redis_client, db)
    status_data = matching_service.get_driver_status(driver_id)
    
    if not status_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Driver status not found. Driver may not have set their availability yet."
        )
    
    response = {
        "driver_id": driver_id,
        "status": status_data["status"],
        "timestamp": status_data["timestamp"]
    }
    
    if "latitude" in status_data and "longitude" in status_data:
        response["location"] = {
            "latitude": status_data["latitude"],
            "longitude": status_data["longitude"]
        }
    
    return DriverStatusResponse(**response)



# Vehicle Management Schemas
class VehicleRegistrationRequest(BaseModel):
    """Request to register or update vehicle information."""
    registration_number: str = Field(..., description="Vehicle registration number")
    make: str = Field(..., description="Vehicle make/manufacturer")
    model: str = Field(..., description="Vehicle model")
    color: str = Field(..., description="Vehicle color")
    insurance_expiry: str = Field(..., description="Insurance expiry date (ISO format)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "registration_number": "MP09AB1234",
                "make": "Maruti Suzuki",
                "model": "Swift",
                "color": "White",
                "insurance_expiry": "2025-12-31T00:00:00"
            }
        }


class VehicleResponse(BaseModel):
    """Response for vehicle information."""
    driver_id: str
    registration_number: str
    make: str
    model: str
    color: str
    insurance_expiry: str
    verified: bool
    message: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "driver_id": "driver123",
                "registration_number": "MP09AB1234",
                "make": "Maruti Suzuki",
                "model": "Swift",
                "color": "White",
                "insurance_expiry": "2025-12-31T00:00:00",
                "verified": False,
                "message": "Vehicle registered successfully"
            }
        }


@router.post("/vehicle", response_model=VehicleResponse, status_code=status.HTTP_201_CREATED)
async def register_vehicle(
    request: VehicleRegistrationRequest,
    driver_id: str,
    db: Session = Depends(get_db)
):
    """
    Register vehicle information for a driver.
    
    - **registration_number**: Vehicle registration number
    - **make**: Vehicle manufacturer
    - **model**: Vehicle model
    - **color**: Vehicle color
    - **insurance_expiry**: Insurance expiry date (must be at least 30 days in future)
    """
    from datetime import datetime, timedelta
    from app.models.user import DriverProfile
    
    # Verify driver exists
    driver = db.query(User).filter(
        User.user_id == driver_id,
        User.user_type == "driver"
    ).first()
    
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Driver not found"
        )
    
    if not driver.driver_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Driver profile not found"
        )
    
    # Parse insurance expiry date
    try:
        insurance_expiry = datetime.fromisoformat(request.insurance_expiry.replace('Z', '+00:00'))
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid insurance expiry date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)"
        )
    
    # Validate insurance expiry is at least 30 days in future
    min_expiry = datetime.utcnow() + timedelta(days=30)
    if insurance_expiry < min_expiry:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insurance must be valid for at least 30 days"
        )
    
    # Update driver profile with vehicle information
    driver.driver_profile.vehicle_registration = request.registration_number
    driver.driver_profile.vehicle_make = request.make
    driver.driver_profile.vehicle_model = request.model
    driver.driver_profile.vehicle_color = request.color
    driver.driver_profile.insurance_expiry = insurance_expiry
    driver.driver_profile.vehicle_verified = False  # Requires verification
    
    db.commit()
    db.refresh(driver.driver_profile)
    
    return VehicleResponse(
        driver_id=driver_id,
        registration_number=driver.driver_profile.vehicle_registration,
        make=driver.driver_profile.vehicle_make,
        model=driver.driver_profile.vehicle_model,
        color=driver.driver_profile.vehicle_color,
        insurance_expiry=driver.driver_profile.insurance_expiry.isoformat(),
        verified=driver.driver_profile.vehicle_verified,
        message="Vehicle registered successfully. Verification required."
    )


@router.put("/vehicle", response_model=VehicleResponse)
async def update_vehicle(
    request: VehicleRegistrationRequest,
    driver_id: str,
    db: Session = Depends(get_db)
):
    """
    Update vehicle information for a driver.
    Vehicle will be marked as unverified and require re-verification.
    
    - **registration_number**: Vehicle registration number
    - **make**: Vehicle manufacturer
    - **model**: Vehicle model
    - **color**: Vehicle color
    - **insurance_expiry**: Insurance expiry date (must be at least 30 days in future)
    """
    from datetime import datetime, timedelta
    from app.models.user import DriverProfile
    
    # Verify driver exists
    driver = db.query(User).filter(
        User.user_id == driver_id,
        User.user_type == "driver"
    ).first()
    
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Driver not found"
        )
    
    if not driver.driver_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Driver profile not found"
        )
    
    # Parse insurance expiry date
    try:
        insurance_expiry = datetime.fromisoformat(request.insurance_expiry.replace('Z', '+00:00'))
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid insurance expiry date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)"
        )
    
    # Validate insurance expiry is at least 30 days in future
    min_expiry = datetime.utcnow() + timedelta(days=30)
    if insurance_expiry < min_expiry:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insurance must be valid for at least 30 days"
        )
    
    # Update driver profile with vehicle information
    driver.driver_profile.vehicle_registration = request.registration_number
    driver.driver_profile.vehicle_make = request.make
    driver.driver_profile.vehicle_model = request.model
    driver.driver_profile.vehicle_color = request.color
    driver.driver_profile.insurance_expiry = insurance_expiry
    driver.driver_profile.vehicle_verified = False  # Mark as unverified, requires re-verification
    
    db.commit()
    db.refresh(driver.driver_profile)
    
    return VehicleResponse(
        driver_id=driver_id,
        registration_number=driver.driver_profile.vehicle_registration,
        make=driver.driver_profile.vehicle_make,
        model=driver.driver_profile.vehicle_model,
        color=driver.driver_profile.vehicle_color,
        insurance_expiry=driver.driver_profile.insurance_expiry.isoformat(),
        verified=driver.driver_profile.vehicle_verified,
        message="Vehicle updated successfully. Re-verification required."
    )


@router.get("/vehicle/{driver_id}", response_model=VehicleResponse)
async def get_vehicle_info(
    driver_id: str,
    db: Session = Depends(get_db)
):
    """
    Get vehicle information for a driver.
    
    - **driver_id**: Driver's user ID
    """
    # Verify driver exists
    driver = db.query(User).filter(
        User.user_id == driver_id,
        User.user_type == "driver"
    ).first()
    
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Driver not found"
        )
    
    if not driver.driver_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Driver profile not found"
        )
    
    if not driver.driver_profile.vehicle_registration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle information not found"
        )
    
    return VehicleResponse(
        driver_id=driver_id,
        registration_number=driver.driver_profile.vehicle_registration,
        make=driver.driver_profile.vehicle_make,
        model=driver.driver_profile.vehicle_model,
        color=driver.driver_profile.vehicle_color,
        insurance_expiry=driver.driver_profile.insurance_expiry.isoformat(),
        verified=driver.driver_profile.vehicle_verified,
        message="Vehicle information retrieved successfully"
    )



# Driver Preferences Endpoints (Requirements: 18.10, 18.11)

class DriverPreferencesRequest(BaseModel):
    """Request to update driver preferences."""
    accept_extended_area: Optional[bool] = Field(None, description="Accept rides in extended area (beyond city limits)")
    accept_parcel_delivery: Optional[bool] = Field(None, description="Accept parcel delivery requests")
    
    class Config:
        json_schema_extra = {
            "example": {
                "accept_extended_area": True,
                "accept_parcel_delivery": True
            }
        }


class DriverPreferencesResponse(BaseModel):
    """Response for driver preferences."""
    driver_id: str
    accept_extended_area: bool
    accept_parcel_delivery: bool
    extended_area_ride_percentage: float
    
    class Config:
        json_schema_extra = {
            "example": {
                "driver_id": "driver123",
                "accept_extended_area": True,
                "accept_parcel_delivery": True,
                "extended_area_ride_percentage": 25.5
            }
        }


@router.put("/preferences", response_model=DriverPreferencesResponse)
async def update_driver_preferences(
    request: DriverPreferencesRequest,
    driver_id: str,
    db: Session = Depends(get_db)
):
    """
    Update driver preferences for extended area and parcel delivery.
    
    - **accept_extended_area**: Whether to accept rides in extended area (beyond city limits)
    - **accept_parcel_delivery**: Whether to accept parcel delivery requests
    
    Requirements: 18.10, 18.11
    """
    # Verify driver exists
    driver = db.query(User).filter(
        User.user_id == driver_id,
        User.user_type == "driver"
    ).first()
    
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Driver not found"
        )
    
    if not driver.driver_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Driver profile not found"
        )
    
    # Update preferences
    if request.accept_extended_area is not None:
        driver.driver_profile.accept_extended_area = request.accept_extended_area
    
    if request.accept_parcel_delivery is not None:
        driver.driver_profile.accept_parcel_delivery = request.accept_parcel_delivery
    
    db.commit()
    db.refresh(driver.driver_profile)
    
    # Calculate extended area ride percentage
    total_rides = driver.driver_profile.total_ride_count
    extended_rides = driver.driver_profile.extended_area_ride_count
    percentage = (extended_rides / total_rides * 100) if total_rides > 0 else 0.0
    
    return DriverPreferencesResponse(
        driver_id=driver_id,
        accept_extended_area=driver.driver_profile.accept_extended_area,
        accept_parcel_delivery=driver.driver_profile.accept_parcel_delivery,
        extended_area_ride_percentage=round(percentage, 2)
    )


@router.get("/preferences", response_model=DriverPreferencesResponse)
async def get_driver_preferences(
    driver_id: str,
    db: Session = Depends(get_db)
):
    """
    Get driver preferences for extended area and parcel delivery.
    
    Requirements: 18.10, 18.12
    """
    # Verify driver exists
    driver = db.query(User).filter(
        User.user_id == driver_id,
        User.user_type == "driver"
    ).first()
    
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Driver not found"
        )
    
    if not driver.driver_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Driver profile not found"
        )
    
    # Calculate extended area ride percentage
    total_rides = driver.driver_profile.total_ride_count
    extended_rides = driver.driver_profile.extended_area_ride_count
    percentage = (extended_rides / total_rides * 100) if total_rides > 0 else 0.0
    
    return DriverPreferencesResponse(
        driver_id=driver_id,
        accept_extended_area=driver.driver_profile.accept_extended_area,
        accept_parcel_delivery=driver.driver_profile.accept_parcel_delivery,
        extended_area_ride_percentage=round(percentage, 2)
    )
