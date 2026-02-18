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


class VerificationSendRequest(BaseModel):
    """Request schema for sending verification code."""
    phone_number: str = Field(..., pattern=r'^\+91\d{10}$')


class VerificationSendResponse(BaseModel):
    """Response schema for verification code sent."""
    session_id: str
    phone_number: str
    expires_at: datetime
    message: str = "Verification code sent successfully"


class VerificationConfirmRequest(BaseModel):
    """Request schema for confirming verification code."""
    session_id: str
    code: str = Field(..., min_length=6, max_length=6, pattern=r'^\d{6}$')


class VerificationConfirmResponse(BaseModel):
    """Response schema for successful verification."""
    session_id: str
    phone_number: str
    verified: bool
    message: str


class LoginRequest(BaseModel):
    """Request schema for user login."""
    phone_number: str = Field(..., pattern=r'^\+91\d{10}$')
    password: str = Field(..., min_length=8, max_length=100)


class LoginResponse(BaseModel):
    """Response schema for successful login."""
    access_token: str
    token_type: str = "bearer"
    user_id: str
    phone_number: str
    name: str
    email: str
    user_type: str
    phone_verified: bool
    message: str = "Login successful"



class IDVerificationResponse(BaseModel):
    """Response schema for ID document verification."""
    driver_id: str
    document_type: str
    document_path: str
    uploaded_at: datetime
    verification_status: str
    message: str = "ID document uploaded successfully and pending verification"
    
    class Config:
        from_attributes = True
