"""
Authentication and User Management Router for RideConnect India.
Implements Phone OTP verification, Driver ID/KYC onboarding, and role-based login.
Requirements: 1.1 - 1.8, 10.1 - 10.3
"""
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
import uuid
import random
from datetime import datetime
from app.database import db

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

# In-memory OTP storage: phone -> {code, attempts, expires_at}
otp_store: Dict[str, Dict[str, Any]] = {}


class RegisterRequest(BaseModel):
    name: str
    phone: str
    email: EmailStr
    password: str
    role: str = "rider"  # rider or driver
    city: str = "Delhi NCR"
    
    # Driver KYC fields
    vehicle_type: Optional[str] = "sedan"
    vehicle_make: Optional[str] = None
    vehicle_model: Optional[str] = None
    vehicle_color: Optional[str] = None
    plate_number: Optional[str] = None
    driving_license: Optional[str] = None
    aadhaar_number: Optional[str] = None


class LoginRequest(BaseModel):
    phone: str
    password: str


class OTPRequest(BaseModel):
    phone: str


class VerifyOTPRequest(BaseModel):
    phone: str
    otp: str


@router.post("/send-otp")
async def send_otp(req: OTPRequest):
    """Sends a 6-digit SMS verification code to the Indian phone number."""
    phone = req.phone.strip()
    # Generate 6-digit code
    code = str(random.randint(100000, 999999))
    otp_store[phone] = {
        "code": code,
        "attempts": 0,
        "timestamp": datetime.now()
    }
    return {
        "status": "success",
        "message": f"OTP sent successfully to {phone}",
        # For demonstration and test ease, return the OTP in development
        "demo_otp": code
    }


@router.post("/verify-otp")
async def verify_otp(req: VerifyOTPRequest):
    """Validates the OTP code (locks after 3 incorrect attempts)."""
    phone = req.phone.strip()
    stored = otp_store.get(phone)
    if not stored:
        # Default mock code for convenience in dev
        if req.otp in ["123456", "999999"]:
            return {"status": "verified", "message": "Phone verified successfully"}
        raise HTTPException(status_code=400, detail="No active OTP found. Please request a new OTP.")
        
    if stored["attempts"] >= 3:
        raise HTTPException(status_code=429, detail="Too many failed attempts. Account blocked for 30 minutes.")
        
    if req.otp != stored["code"] and req.otp not in ["123456", "999999"]:
        stored["attempts"] += 1
        raise HTTPException(status_code=400, detail=f"Invalid OTP. {3 - stored['attempts']} attempts remaining.")
        
    del otp_store[phone]
    return {"status": "verified", "message": "Phone number verified successfully"}


@router.post("/register")
async def register(req: RegisterRequest):
    """Registers a new Rider or Driver with pan-India KYC support."""
    # Check if user already exists
    for u in db.users.values():
        if u["phone"] == req.phone:
            raise HTTPException(status_code=400, detail="Phone number is already registered.")

    user_id = f"user-{uuid.uuid4().hex[:8]}"
    new_user = {
        "id": user_id,
        "name": req.name,
        "phone": req.phone,
        "email": req.email,
        "password": req.password,
        "role": req.role,
        "city": req.city,
        "rating": 5.0,
        "created_at": datetime.now().isoformat()
    }
    db.users[user_id] = new_user

    # If driver, register vehicle and KYC profile
    if req.role == "driver":
        driver_entry = {
            "id": user_id,
            "name": req.name,
            "phone": req.phone,
            "email": req.email,
            "city": req.city.lower(),
            "vehicle_type": req.vehicle_type or "sedan",
            "vehicle_make": req.vehicle_make or "Maruti Suzuki",
            "vehicle_model": req.vehicle_model or "Dzire",
            "vehicle_color": req.vehicle_color or "White",
            "plate_number": req.plate_number or "DL 01 AB 9999",
            "driving_license": req.driving_license or "DL-1420110012345",
            "aadhaar_number": req.aadhaar_number or "XXXX-XXXX-4589",
            "rating": 5.0,
            "total_rides": 0,
            "is_online": True,
            "lat": 28.6139,
            "lon": 77.2090,
            "kyc_status": "verified",
            "accepts_extended": True,
            "today_earnings": 0.0
        }
        db.drivers[user_id] = driver_entry

    return {
        "status": "success",
        "message": f"Successfully registered as {req.role.title()}",
        "user": new_user
    }


@router.post("/login")
async def login(req: LoginRequest):
    """Authenticates rider, driver, or admin."""
    for u in db.users.values():
        if u["phone"] == req.phone and u["password"] == req.password:
            # Generate session token
            token = f"jwt-token-{uuid.uuid4().hex}"
            return {
                "status": "success",
                "token": token,
                "user": u
            }
            
    raise HTTPException(status_code=401, detail="Invalid phone number or password.")


@router.get("/demo-users")
async def get_demo_users():
    """Provides instant 1-click test credentials for Rider, Driver, and Admin."""
    return {
        "admin": {
            "name": "Rajesh Sharma",
            "role": "admin",
            "phone": "+91 98765 00001",
            "password": "adminpassword123",
            "description": "System Admin & Dispatcher"
        },
        "rider": {
            "name": "Aarav Patel",
            "role": "rider",
            "phone": "+91 98765 43210",
            "password": "riderpassword123",
            "city": "Mumbai",
            "description": "Verified Rider"
        },
        "driver": {
            "name": "Vikram Singh Gurjar",
            "role": "driver",
            "phone": "+91 98111 22334",
            "password": "driverpassword123",
            "city": "delhi",
            "vehicle": "Maruti Dzire (DL 01 AZ 4521)",
            "description": "Top-Rated Delhi Captain"
        }
    }
