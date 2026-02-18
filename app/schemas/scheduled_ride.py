"""
Pydantic schemas for scheduled rides.
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict
from datetime import datetime


class LocationSchema(BaseModel):
    """Location schema for pickup and destination."""
    latitude: float = Field(..., description="Latitude coordinate")
    longitude: float = Field(..., description="Longitude coordinate")
    address: Optional[str] = Field(None, description="Human-readable address")


class FareBreakdownSchema(BaseModel):
    """Fare breakdown schema."""
    base: float
    per_km: float
    distance: float
    surge: float


class ScheduledRideRequest(BaseModel):
    """Request to create a scheduled ride."""
    pickup_location: LocationSchema
    destination: LocationSchema
    scheduled_pickup_time: datetime = Field(..., description="Scheduled pickup time (ISO format)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "pickup_location": {
                    "latitude": 22.7196,
                    "longitude": 75.8577,
                    "address": "Rajwada, Indore"
                },
                "destination": {
                    "latitude": 22.7532,
                    "longitude": 75.8937,
                    "address": "Treasure Island Mall, Indore"
                },
                "scheduled_pickup_time": "2026-02-20T10:00:00"
            }
        }


class ScheduledRideUpdate(BaseModel):
    """Request to update a scheduled ride."""
    pickup_location: Optional[LocationSchema] = None
    destination: Optional[LocationSchema] = None
    scheduled_pickup_time: Optional[datetime] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "scheduled_pickup_time": "2026-02-20T11:00:00"
            }
        }


class ScheduledRideResponse(BaseModel):
    """Response for scheduled ride operations."""
    ride_id: str
    rider_id: str
    driver_id: Optional[str]
    pickup_location: Dict
    destination: Dict
    scheduled_pickup_time: datetime
    estimated_fare: float
    fare_breakdown: Dict
    status: str
    created_at: datetime
    modified_at: Optional[datetime]
    matched_at: Optional[datetime]
    
    class Config:
        json_schema_extra = {
            "example": {
                "ride_id": "sched_ride_123",
                "rider_id": "rider_456",
                "driver_id": None,
                "pickup_location": {
                    "latitude": 22.7196,
                    "longitude": 75.8577,
                    "address": "Rajwada, Indore"
                },
                "destination": {
                    "latitude": 22.7532,
                    "longitude": 75.8937,
                    "address": "Treasure Island Mall, Indore"
                },
                "scheduled_pickup_time": "2026-02-20T10:00:00",
                "estimated_fare": 150.0,
                "fare_breakdown": {
                    "base": 30.0,
                    "per_km": 12.0,
                    "distance": 10.0,
                    "surge": 1.0
                },
                "status": "scheduled",
                "created_at": "2026-02-19T15:30:00",
                "modified_at": None,
                "matched_at": None
            }
        }
