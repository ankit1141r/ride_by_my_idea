"""
Pydantic schemas for location API endpoints.
"""
from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional


class DriverLocationUpdate(BaseModel):
    """
    Schema for driver location update request.
    
    Requirements: 4.4, 8.1, 8.2
    """
    latitude: float = Field(
        ...,
        description="Latitude coordinate",
        ge=-90,
        le=90,
        example=22.7196
    )
    longitude: float = Field(
        ...,
        description="Longitude coordinate",
        ge=-180,
        le=180,
        example=75.8577
    )
    address: Optional[str] = Field(
        None,
        description="Human-readable address",
        max_length=500,
        example="Vijay Nagar, Indore, Madhya Pradesh"
    )
    status: Optional[str] = Field(
        None,
        description="Driver status: available, unavailable, busy",
        example="available"
    )
    accuracy: Optional[float] = Field(
        None,
        description="Location accuracy in meters",
        ge=0,
        example=10.5
    )
    
    @validator('status')
    def validate_status(cls, v):
        """Validate driver status."""
        if v is not None:
            valid_statuses = ['available', 'unavailable', 'busy']
            if v not in valid_statuses:
                raise ValueError(f'Status must be one of: {", ".join(valid_statuses)}')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "latitude": 22.7196,
                "longitude": 75.8577,
                "address": "Vijay Nagar, Indore, Madhya Pradesh",
                "status": "available",
                "accuracy": 10.5
            }
        }


class DriverLocationResponse(BaseModel):
    """
    Schema for driver location response.
    
    Requirements: 8.1
    """
    user_id: str = Field(..., description="Driver's user ID")
    latitude: float = Field(..., description="Latitude coordinate")
    longitude: float = Field(..., description="Longitude coordinate")
    address: Optional[str] = Field(None, description="Human-readable address")
    status: Optional[str] = Field(None, description="Driver status")
    accuracy: Optional[float] = Field(None, description="Location accuracy in meters")
    timestamp: datetime = Field(..., description="When location was recorded")
    message: str = Field(..., description="Response message")
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "driver123",
                "latitude": 22.7196,
                "longitude": 75.8577,
                "address": "Vijay Nagar, Indore, Madhya Pradesh",
                "status": "available",
                "accuracy": 10.5,
                "timestamp": "2024-01-15T10:30:00Z",
                "message": "Location updated successfully"
            }
        }


class LocationValidationResponse(BaseModel):
    """
    Schema for location validation response.
    
    Requirements: 2.4, 13.6
    """
    valid: bool = Field(..., description="Whether location is within service area")
    message: str = Field(..., description="Validation message")
    latitude: float = Field(..., description="Latitude coordinate")
    longitude: float = Field(..., description="Longitude coordinate")
    
    class Config:
        json_schema_extra = {
            "example": {
                "valid": True,
                "message": "Location is within service area",
                "latitude": 22.7196,
                "longitude": 75.8577
            }
        }
