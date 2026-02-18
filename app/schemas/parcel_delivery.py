"""
Parcel Delivery schemas for request/response validation.
"""
from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime


class LocationSchema(BaseModel):
    """Location schema for pickup and delivery."""
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    address: Optional[str] = None


class ParcelDeliveryRequest(BaseModel):
    """Request schema for creating a parcel delivery."""
    pickup_location: LocationSchema
    delivery_location: LocationSchema
    recipient_phone: str = Field(..., min_length=10, max_length=15)
    recipient_name: str = Field(..., min_length=1, max_length=100)
    parcel_size: str = Field(..., pattern="^(small|medium|large)$")
    weight_kg: float = Field(..., gt=0, le=30)
    description: Optional[str] = Field(None, max_length=500)
    special_instructions: Optional[str] = None
    is_fragile: bool = False
    is_urgent: bool = False
    
    @validator('weight_kg')
    def validate_weight(cls, v):
        if v > 30:
            raise ValueError('Weight cannot exceed 30kg')
        return v


class ParcelPickupConfirmation(BaseModel):
    """Request schema for confirming parcel pickup."""
    pickup_photo: str  # Base64 encoded image or URL
    pickup_signature: Optional[str] = None  # Base64 encoded signature or text


class ParcelDeliveryConfirmation(BaseModel):
    """Request schema for confirming parcel delivery."""
    delivery_signature: str  # Base64 encoded signature or text
    delivery_photo: Optional[str] = None  # Base64 encoded image or URL


class ParcelDeliveryResponse(BaseModel):
    """Response schema for parcel delivery."""
    delivery_id: str
    sender_id: str
    recipient_phone: str
    recipient_name: str
    driver_id: Optional[str]
    pickup_location: dict
    delivery_location: dict
    parcel_size: str
    weight_kg: float
    description: Optional[str]
    special_instructions: Optional[str]
    is_fragile: bool
    is_urgent: bool
    estimated_fare: float
    fare_breakdown: dict
    final_fare: Optional[float]
    status: str
    created_at: datetime
    matched_at: Optional[datetime]
    picked_up_at: Optional[datetime]
    delivered_at: Optional[datetime]
    estimated_delivery_time: Optional[datetime]
    payment_status: str
    
    class Config:
        from_attributes = True
