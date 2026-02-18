"""
Authentication router for user registration and login.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Form, File, UploadFile
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import bcrypt
import uuid
from datetime import datetime

from app.database import get_db
from app.schemas.auth import (
    UserRegistrationRequest,
    UserRegistrationResponse,
    VerificationSendRequest,
    VerificationSendResponse,
    VerificationConfirmRequest,
    VerificationConfirmResponse,
    LoginRequest,
    LoginResponse,
    ErrorResponse,
    IDVerificationResponse
)
from app.models.user import User, DriverProfile, UserType, DriverStatus
from app.models.verification import VerificationSession
import random

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



def generate_otp() -> str:
    """Generate a random 6-digit OTP code."""
    return ''.join([str(random.randint(0, 9)) for _ in range(6)])


def send_sms(phone_number: str, message: str) -> bool:
    """
    Send SMS via Twilio gateway.
    In production, this would use the actual Twilio API.
    For testing, this is a mock implementation.
    """
    from app.config import settings
    
    # Mock implementation for testing
    if settings.app_env == "testing":
        print(f"[MOCK SMS] To: {phone_number}, Message: {message}")
        return True
    
    # Production implementation with Twilio
    try:
        from twilio.rest import Client
        
        if not settings.twilio_account_sid or not settings.twilio_auth_token:
            print(f"[WARNING] Twilio credentials not configured. SMS not sent to {phone_number}")
            return False
        
        client = Client(settings.twilio_account_sid, settings.twilio_auth_token)
        
        message = client.messages.create(
            body=message,
            from_=settings.twilio_phone_number,
            to=phone_number
        )
        
        return message.sid is not None
    except Exception as e:
        print(f"[ERROR] Failed to send SMS: {str(e)}")
        return False


@router.post(
    "/verify/send",
    response_model=VerificationSendResponse,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid phone number"},
        429: {"model": ErrorResponse, "description": "Too many attempts, blocked"}
    }
)
async def send_verification_code(
    request: VerificationSendRequest,
    db: Session = Depends(get_db)
):
    """
    Send a verification code to the provided phone number via SMS.
    
    - **phone_number**: Phone number in format +91XXXXXXXXXX
    
    Generates a 6-digit OTP code and sends it via SMS.
    The code expires after 10 minutes.
    After 3 failed verification attempts, the phone number is blocked for 30 minutes.
    """
    phone_number = request.phone_number
    
    # Check if there's an active blocked session for this phone number
    existing_session = db.query(VerificationSession).filter(
        VerificationSession.phone_number == phone_number
    ).order_by(VerificationSession.created_at.desc()).first()
    
    if existing_session and existing_session.is_blocked():
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Too many failed attempts. Please try again after {existing_session.blocked_until.isoformat()}"
        )
    
    # Generate OTP code
    otp_code = generate_otp()
    
    # Create new verification session
    session_id = str(uuid.uuid4())
    new_session = VerificationSession.create_session(
        phone_number=phone_number,
        code=otp_code,
        session_id=session_id
    )
    
    try:
        db.add(new_session)
        db.commit()
        db.refresh(new_session)
        
        # Send SMS with OTP
        sms_message = f"Your verification code is: {otp_code}. This code expires in 10 minutes."
        sms_sent = send_sms(phone_number, sms_message)
        
        if not sms_sent:
            # Log warning but don't fail the request
            print(f"[WARNING] SMS not sent to {phone_number}, but session created")
        
        return VerificationSendResponse(
            session_id=new_session.session_id,
            phone_number=new_session.phone_number,
            expires_at=new_session.expires_at
        )
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create verification session: {str(e)}"
        )


@router.post(
    "/verify/confirm",
    response_model=VerificationConfirmResponse,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid code or session"},
        404: {"model": ErrorResponse, "description": "Session not found"},
        410: {"model": ErrorResponse, "description": "Session expired"},
        429: {"model": ErrorResponse, "description": "Too many attempts, blocked"}
    }
)
async def confirm_verification_code(
    request: VerificationConfirmRequest,
    db: Session = Depends(get_db)
):
    """
    Confirm a verification code for a given session.
    
    - **session_id**: The verification session ID from the send endpoint
    - **code**: The 6-digit verification code received via SMS
    
    Validates the code and marks the phone number as verified.
    Maximum 3 attempts allowed. After 3 failed attempts, blocks for 30 minutes.
    """
    session_id = request.session_id
    code = request.code
    
    # Find the verification session
    session = db.query(VerificationSession).filter(
        VerificationSession.session_id == session_id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Verification session not found"
        )
    
    # Check if already verified
    if session.verified:
        return VerificationConfirmResponse(
            session_id=session.session_id,
            phone_number=session.phone_number,
            verified=True,
            message="Phone number already verified"
        )
    
    # Check if expired
    if session.is_expired():
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="Verification code has expired. Please request a new code."
        )
    
    # Check if blocked
    if session.is_blocked():
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Too many failed attempts. Please try again after {session.blocked_until.isoformat()}"
        )
    
    # Check if can attempt
    if not session.can_attempt_verification():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot verify at this time. Maximum attempts reached or session expired."
        )
    
    # Verify the code
    if session.code != code:
        # Increment attempts and potentially block
        session.increment_attempts()
        db.commit()
        
        remaining_attempts = 3 - session.attempts
        if remaining_attempts > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid verification code. {remaining_attempts} attempts remaining."
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many failed attempts. Your phone number has been blocked for 30 minutes."
            )
    
    # Code is correct - mark as verified
    session.verified = True
    
    # Update user's phone_verified status
    user = db.query(User).filter(
        User.phone_number == session.phone_number
    ).first()
    
    if user:
        user.phone_verified = True
    
    try:
        db.commit()
        db.refresh(session)
        
        return VerificationConfirmResponse(
            session_id=session.session_id,
            phone_number=session.phone_number,
            verified=True,
            message="Phone number verified successfully"
        )
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to confirm verification: {str(e)}"
        )


@router.post(
    "/login",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid credentials"},
        401: {"model": ErrorResponse, "description": "Authentication failed"}
    }
)
async def login(
    credentials: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Authenticate user and generate JWT access token.
    
    - **phone_number**: Phone number in format +91XXXXXXXXXX
    - **password**: User's password
    
    Returns JWT access token and user information.
    The token includes user_id, user_type, and phone_verified claims.
    Session is stored in Redis with expiration.
    """
    from app.database import redis_client
    from app.utils.jwt import create_access_token
    from datetime import timedelta
    
    # Find user by phone number
    user = db.query(User).filter(
        User.phone_number == credentials.phone_number
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid phone number or password"
        )
    
    # Verify password
    if not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid phone number or password"
        )
    
    # Generate JWT token
    access_token = create_access_token(
        user_id=user.user_id,
        user_type=user.user_type.value,
        phone_verified=user.phone_verified
    )
    
    # Store session in Redis
    session_key = f"session:{user.user_id}"
    session_data = {
        "user_id": user.user_id,
        "phone_number": user.phone_number,
        "user_type": user.user_type.value,
        "phone_verified": str(user.phone_verified),
        "login_time": datetime.utcnow().isoformat()
    }
    
    # Store session with expiration matching JWT token expiration
    from app.config import settings
    expiration_seconds = settings.jwt_access_token_expire_minutes * 60
    
    # Use Redis hash to store session data
    redis_client.hset(session_key, mapping=session_data)
    redis_client.expire(session_key, expiration_seconds)
    
    return LoginResponse(
        access_token=access_token,
        user_id=user.user_id,
        phone_number=user.phone_number,
        name=user.name,
        email=user.email,
        user_type=user.user_type.value,
        phone_verified=user.phone_verified
    )



@router.post(
    "/driver/verify-id",
    response_model=IDVerificationResponse,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid file or request"},
        404: {"model": ErrorResponse, "description": "Driver not found"},
        413: {"model": ErrorResponse, "description": "File too large"}
    }
)
async def verify_driver_id(
    user_id: str = Form(...),
    document_type: str = Form(..., pattern=r'^(drivers_license|aadhaar|pan)$'),
    document: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload and verify ID document for driver.
    
    - **user_id**: Driver's user ID
    - **document_type**: Type of document (drivers_license, aadhaar, or pan)
    - **document**: Image file (JPEG, PNG, PDF)
    
    Validates file type and size, stores document, and initiates verification.
    Maximum file size: 5MB
    Allowed formats: image/jpeg, image/png, application/pdf
    """
    from fastapi import Form, File, UploadFile
    import os
    from pathlib import Path
    
    # Validate user exists and is a driver
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if user.user_type != UserType.DRIVER:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only drivers can upload ID documents"
        )
    
    # Get driver profile
    driver_profile = db.query(DriverProfile).filter(
        DriverProfile.driver_id == user_id
    ).first()
    
    if not driver_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Driver profile not found"
        )
    
    # Validate file type
    allowed_content_types = ["image/jpeg", "image/png", "application/pdf"]
    if document.content_type not in allowed_content_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed types: {', '.join(allowed_content_types)}"
        )
    
    # Validate file size (5MB max)
    max_size = 5 * 1024 * 1024  # 5MB in bytes
    file_content = await document.read()
    file_size = len(file_content)
    
    if file_size > max_size:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Maximum size: 5MB, uploaded: {file_size / (1024 * 1024):.2f}MB"
        )
    
    if file_size == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Empty file uploaded"
        )
    
    # Create uploads directory if it doesn't exist
    upload_dir = Path("uploads/id_documents")
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate unique filename
    file_extension = document.filename.split('.')[-1] if '.' in document.filename else 'jpg'
    filename = f"{user_id}_{document_type}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.{file_extension}"
    file_path = upload_dir / filename
    
    # Save file
    try:
        with open(file_path, "wb") as f:
            f.write(file_content)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file: {str(e)}"
        )
    
    # Update driver profile with document metadata
    driver_profile.id_document_path = str(file_path)
    driver_profile.id_document_type = document_type
    driver_profile.id_document_uploaded_at = datetime.utcnow()
    driver_profile.id_verification_status = "pending"
    
    try:
        db.commit()
        db.refresh(driver_profile)
        
        return IDVerificationResponse(
            driver_id=driver_profile.driver_id,
            document_type=driver_profile.id_document_type,
            document_path=driver_profile.id_document_path,
            uploaded_at=driver_profile.id_document_uploaded_at,
            verification_status=driver_profile.id_verification_status
        )
    
    except Exception as e:
        db.rollback()
        # Clean up uploaded file if database update fails
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update driver profile: {str(e)}"
        )
