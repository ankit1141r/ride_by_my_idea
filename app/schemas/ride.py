"""
Pydantic schemas for ride API endpoints.
"""
from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional, Dict, Any


class LocationInput(BaseModel):
    """
    Schema for location input in ride requests.
    
    Requirements: 2.1
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
    address: str = Field(
        ...,
        description="Human-readable address",
        min_length=1,
        max_length=500,
        example="Vijay Nagar, Indore, Madhya Pradesh"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "latitude": 22.7196,
                "longitude": 75.8577,
                "address": "Vijay Nagar, Indore, Madhya Pradesh"
            }
        }


class RideRequestCreate(BaseModel):
    """
    Schema for creating a ride request.
    
    Requirements: 2.1, 2.2
    """
    pickup_location: LocationInput = Field(
        ...,
        description="Pickup location with coordinates and address"
    )
    destination: LocationInput = Field(
        ...,
        description="Destination location with coordinates and address"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "pickup_location": {
                    "latitude": 22.7196,
                    "longitude": 75.8577,
                    "address": "Vijay Nagar, Indore, Madhya Pradesh"
                },
                "destination": {
                    "latitude": 22.7520,
                    "longitude": 75.8937,
                    "address": "Rajwada, Indore, Madhya Pradesh"
                }
            }
        }


class FareBreakdownResponse(BaseModel):
    """
    Schema for fare breakdown in response.
    
    Requirements: 5.3
    """
    base: float = Field(..., description="Base fare in ₹")
    per_km: float = Field(..., description="Rate per kilometer in ₹")
    distance: float = Field(..., description="Distance in kilometers")
    surge: float = Field(..., description="Surge multiplier")
    
    class Config:
        json_schema_extra = {
            "example": {
                "base": 30.0,
                "per_km": 12.0,
                "distance": 5.5,
                "surge": 1.0
            }
        }


class RideRequestResponse(BaseModel):
    """
    Schema for ride request creation response.
    
    Requirements: 2.1, 2.2, 2.5
    """
    request_id: str = Field(..., description="Unique ride request ID")
    estimated_fare: float = Field(..., description="Estimated fare in ₹")
    estimated_arrival: int = Field(..., description="Estimated arrival time in minutes")
    fare_breakdown: FareBreakdownResponse = Field(..., description="Detailed fare breakdown")
    pickup_location: Dict[str, Any] = Field(..., description="Pickup location details")
    destination: Dict[str, Any] = Field(..., description="Destination details")
    requested_at: datetime = Field(..., description="When the request was created")
    status: str = Field(..., description="Current request status")
    message: str = Field(..., description="Response message")
    
    class Config:
        json_schema_extra = {
            "example": {
                "request_id": "ride_123456789",
                "estimated_fare": 96.0,
                "estimated_arrival": 8,
                "fare_breakdown": {
                    "base": 30.0,
                    "per_km": 12.0,
                    "distance": 5.5,
                    "surge": 1.0
                },
                "pickup_location": {
                    "latitude": 22.7196,
                    "longitude": 75.8577,
                    "address": "Vijay Nagar, Indore, Madhya Pradesh"
                },
                "destination": {
                    "latitude": 22.7520,
                    "longitude": 75.8937,
                    "address": "Rajwada, Indore, Madhya Pradesh"
                },
                "requested_at": "2024-01-15T10:30:00Z",
                "status": "requested",
                "message": "Ride request created successfully"
            }
        }


class RideHistoryItem(BaseModel):
    """
    Schema for a single ride in history list.
    
    Requirements: 9.2, 9.3
    """
    ride_id: str = Field(..., description="Unique ride identifier")
    date: datetime = Field(..., description="Ride date and time")
    pickup_location: Dict[str, Any] = Field(..., description="Pickup location details")
    destination: Dict[str, Any] = Field(..., description="Destination details")
    fare: float = Field(..., description="Final fare (or estimated if not completed)")
    status: str = Field(..., description="Ride status")
    driver_rating: Optional[int] = Field(None, description="Rating given to driver (1-5)")
    rider_rating: Optional[int] = Field(None, description="Rating given to rider (1-5)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "ride_id": "ride_123456789",
                "date": "2024-01-15T10:30:00Z",
                "pickup_location": {
                    "latitude": 22.7196,
                    "longitude": 75.8577,
                    "address": "Vijay Nagar, Indore"
                },
                "destination": {
                    "latitude": 22.7520,
                    "longitude": 75.8937,
                    "address": "Rajwada, Indore"
                },
                "fare": 96.0,
                "status": "completed",
                "driver_rating": 5,
                "rider_rating": 4
            }
        }


class RideHistoryResponse(BaseModel):
    """
    Schema for ride history list response.
    
    Requirements: 9.1, 9.2, 9.3
    """
    rides: list[RideHistoryItem] = Field(..., description="List of rides in reverse chronological order")
    total: int = Field(..., description="Total number of rides matching filters")
    
    class Config:
        json_schema_extra = {
            "example": {
                "rides": [
                    {
                        "ride_id": "ride_123456789",
                        "date": "2024-01-15T10:30:00Z",
                        "pickup_location": {
                            "latitude": 22.7196,
                            "longitude": 75.8577,
                            "address": "Vijay Nagar, Indore"
                        },
                        "destination": {
                            "latitude": 22.7520,
                            "longitude": 75.8937,
                            "address": "Rajwada, Indore"
                        },
                        "fare": 96.0,
                        "status": "completed",
                        "driver_rating": 5,
                        "rider_rating": None
                    }
                ],
                "total": 1
            }
        }


class RideDetailsResponse(BaseModel):
    """
    Schema for detailed ride view.
    
    Requirements: 9.3, 9.5
    """
    ride_id: str = Field(..., description="Unique ride identifier")
    rider_id: str = Field(..., description="Rider user ID")
    driver_id: Optional[str] = Field(None, description="Driver user ID")
    status: str = Field(..., description="Ride status")
    
    # Locations
    pickup_location: Dict[str, Any] = Field(..., description="Pickup location details")
    destination: Dict[str, Any] = Field(..., description="Destination details")
    actual_route: Optional[list[Dict[str, Any]]] = Field(None, description="Actual route taken")
    
    # Timing
    requested_at: datetime = Field(..., description="When ride was requested")
    matched_at: Optional[datetime] = Field(None, description="When driver was matched")
    pickup_time: Optional[datetime] = Field(None, description="When driver arrived at pickup")
    start_time: Optional[datetime] = Field(None, description="When ride started")
    completed_at: Optional[datetime] = Field(None, description="When ride completed")
    
    # Fare
    estimated_fare: float = Field(..., description="Estimated fare")
    final_fare: Optional[float] = Field(None, description="Final fare charged")
    fare_breakdown: Dict[str, Any] = Field(..., description="Fare breakdown details")
    
    # Payment
    payment_status: str = Field(..., description="Payment status")
    transaction_id: Optional[str] = Field(None, description="Payment transaction ID")
    
    # Ratings
    rider_rating: Optional[int] = Field(None, description="Rating given to rider")
    rider_review: Optional[str] = Field(None, description="Review text for rider")
    driver_rating: Optional[int] = Field(None, description="Rating given to driver")
    driver_review: Optional[str] = Field(None, description="Review text for driver")
    
    # Cancellation
    cancelled_by: Optional[str] = Field(None, description="User ID who cancelled")
    cancellation_reason: Optional[str] = Field(None, description="Cancellation reason")
    cancellation_fee: Optional[float] = Field(None, description="Cancellation fee charged")
    
    class Config:
        json_schema_extra = {
            "example": {
                "ride_id": "ride_123456789",
                "rider_id": "user_abc123",
                "driver_id": "user_def456",
                "status": "completed",
                "pickup_location": {
                    "latitude": 22.7196,
                    "longitude": 75.8577,
                    "address": "Vijay Nagar, Indore"
                },
                "destination": {
                    "latitude": 22.7520,
                    "longitude": 75.8937,
                    "address": "Rajwada, Indore"
                },
                "actual_route": None,
                "requested_at": "2024-01-15T10:30:00Z",
                "matched_at": "2024-01-15T10:32:00Z",
                "pickup_time": "2024-01-15T10:40:00Z",
                "start_time": "2024-01-15T10:42:00Z",
                "completed_at": "2024-01-15T11:00:00Z",
                "estimated_fare": 96.0,
                "final_fare": 96.0,
                "fare_breakdown": {
                    "base": 30.0,
                    "per_km": 12.0,
                    "distance": 5.5,
                    "surge": 1.0,
                    "total": 96.0
                },
                "payment_status": "completed",
                "transaction_id": "txn_xyz789",
                "rider_rating": 4,
                "rider_review": "Good driver",
                "driver_rating": 5,
                "driver_review": "Polite passenger",
                "cancelled_by": None,
                "cancellation_reason": None,
                "cancellation_fee": None
            }
        }


class ErrorResponse(BaseModel):
    """
    Schema for error responses.
    """
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "boundary_violation",
                "message": "Location is outside Indore service area. Service is only available within Indore city limits.",
                "details": {
                    "location_type": "pickup",
                    "latitude": 23.0,
                    "longitude": 76.0
                }
            }
        }
