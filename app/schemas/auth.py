"""
Authentication schemas for user registration and login.
"""
from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator
from typing import Optional
from datetime import datetime


class VehicleInfo(BaseModel):
    """Vehicle information for driver registration."""
    registration_number: str = Field(..., min_length=1, max_length=50)
    make: str = Field(..., min_length=1, max_length=50)
    model: str = Field(..., min_length=1, max_length=50)
    color: str = Field(..., min_length=1, max_length=30)
    license_number: str = Field(..., min_length=1, max_length=50)
    insurance_expiry: datetime
    
    @field_validator('insurance_expiry', mode='before')
    @classmethod
    def validate_insurance_expiry(cls, v):
        """Validate insurance expiry is at least 30 days in future."""
        if v is None:
            return v
        
        if isinstance(v, str):
            v = datetime.fromisoformat(v.replace('Z', '+00:00'))
        
        from datetime import timedelta
        # Use date comparison to avoid timing issues with exact timestamps
        today = datetime.utcnow().date()
        min_expiry_date = today + timedelta(days=30)
        
        if v.date() < min_expiry_date:
            raise ValueError('Insurance must be valid for at least 30 days')
        return v


class UserRegistrationRequest(BaseModel):
    """Request schema for user registration."""
    phone_number: str = Field(..., pattern=r'^\+91\d{10}$')
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    user_type: str = Field(..., pattern=r'^(rider|driver)$')
    vehicle_info: Optional[VehicleInfo] = None
    
    @model_validator(mode='after')
    def validate_driver_vehicle(self):
        """Validate that drivers provide vehicle information."""
        if self.user_type == 'driver' and self.vehicle_info is None:
            raise ValueError('Vehicle information is required for driver registration')
        if self.user_type == 'rider' and self.vehicle_info is not None:
            raise ValueError('Vehicle information should not be provided for rider registration')
        return self


class UserRegistrationResponse(BaseModel):
    """Response schema for successful user registration."""
    user_id: str
    phone_number: str
    name: str
    email: str
    user_type: str
    phone_verified: bool
    created_at: datetime
    message: str = "User registered successfully. Please verify your phone number."
    
    class Config:
        from_attributes = True


class ErrorResponse(BaseModel):
    """Error response schema."""
    detail: str
