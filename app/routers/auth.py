"""
Authentication router for user registration and login.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import bcrypt
import uuid
from datetime import datetime

from app.database import get_db
from app.schemas.auth import (
    UserRegistrationRequest,
    UserRegistrationResponse,
    ErrorResponse
)
from app.models.user import User, DriverProfile, UserType, DriverStatus

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return bcrypt.checkpw(
        plain_password.encode('utf-8'),
        hashed_password.encode('utf-8')
    )


@router.post(
    "/register",
    response_model=UserRegistrationResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid input data"},
        409: {"model": ErrorResponse, "description": "User already exists"}
    }
)
async def register_user(
    registration_data: UserRegistrationRequest,
    db: Session = Depends(get_db)
):
    """
    Register a new user (rider or driver).
    
    - **phone_number**: Phone number in format +91XXXXXXXXXX
    - **name**: User's full name
    - **email**: User's email address
    - **password**: Password (min 8 characters)
    - **user_type**: Either 'rider' or 'driver'
    - **vehicle_info**: Required for drivers, includes vehicle and license details
    
    Returns the created user information.
    """
    # Check if user already exists
    existing_user = db.query(User).filter(
        User.phone_number == registration_data.phone_number
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this phone number already exists"
        )
    
    # Check if email already exists
    existing_email = db.query(User).filter(
        User.email == registration_data.email
    ).first()
    
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists"
        )
    
    # Hash the password
    password_hash = hash_password(registration_data.password)
    
    # Create user
    user_id = str(uuid.uuid4())
    new_user = User(
        user_id=user_id,
        phone_number=registration_data.phone_number,
        phone_verified=False,
        name=registration_data.name,
        email=registration_data.email,
        user_type=UserType.DRIVER if registration_data.user_type == 'driver' else UserType.RIDER,
        password_hash=password_hash,
        created_at=datetime.utcnow()
    )
    
    try:
        db.add(new_user)
        
        # If driver, create driver profile
        if registration_data.user_type == 'driver' and registration_data.vehicle_info:
            driver_profile = DriverProfile(
                driver_id=user_id,
                license_number=registration_data.vehicle_info.license_number,
                license_verified=False,
                vehicle_registration=registration_data.vehicle_info.registration_number,
                vehicle_make=registration_data.vehicle_info.make,
                vehicle_model=registration_data.vehicle_info.model,
                vehicle_color=registration_data.vehicle_info.color,
                vehicle_verified=False,
                insurance_expiry=registration_data.vehicle_info.insurance_expiry,
                status=DriverStatus.UNAVAILABLE
            )
            db.add(driver_profile)
        
        db.commit()
        db.refresh(new_user)
        
        return UserRegistrationResponse(
            user_id=new_user.user_id,
            phone_number=new_user.phone_number,
            name=new_user.name,
            email=new_user.email,
            user_type=new_user.user_type.value,
            phone_verified=new_user.phone_verified,
            created_at=new_user.created_at
        )
    
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User registration failed due to data conflict"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during registration: {str(e)}"
        )
