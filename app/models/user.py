"""
User models for the ride-hailing platform.
Includes User, DriverProfile, and EmergencyContact models.
"""
from sqlalchemy import Column, String, Boolean, DateTime, Float, Integer, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.database import Base


class UserType(str, enum.Enum):
    """User type enumeration."""
    RIDER = "rider"
    DRIVER = "driver"


class DriverStatus(str, enum.Enum):
    """Driver availability status."""
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    BUSY = "busy"


class User(Base):
    """User model for both riders and drivers."""
    __tablename__ = "users"
    
    user_id = Column(String(36), primary_key=True)
    phone_number = Column(String(15), unique=True, nullable=False, index=True)
    phone_verified = Column(Boolean, default=False, nullable=False)
    name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False)
    user_type = Column(SQLEnum(UserType), nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Ratings
    average_rating = Column(Float, default=0.0)
    total_rides = Column(Integer, default=0)
    
    # Relationships
    driver_profile = relationship("DriverProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    emergency_contacts = relationship("EmergencyContact", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(user_id={self.user_id}, name={self.name}, type={self.user_type})>"


class DriverProfile(Base):
    """Driver-specific profile information."""
    __tablename__ = "driver_profiles"
    
    driver_id = Column(String(36), ForeignKey("users.user_id"), primary_key=True)
    
    # License information
    license_number = Column(String(50), nullable=False)
    license_verified = Column(Boolean, default=False)
    
    # ID document information
    id_document_path = Column(String(500), nullable=True)
    id_document_type = Column(String(50), nullable=True)
    id_document_uploaded_at = Column(DateTime, nullable=True)
    id_verification_status = Column(String(20), default="pending")
    
    # Vehicle information
    vehicle_registration = Column(String(50), nullable=False)
    vehicle_make = Column(String(50), nullable=False)
    vehicle_model = Column(String(50), nullable=False)
    vehicle_color = Column(String(30), nullable=False)
    vehicle_verified = Column(Boolean, default=False)
    insurance_expiry = Column(DateTime, nullable=False)
    
    # Driver status
    status = Column(SQLEnum(DriverStatus), default=DriverStatus.UNAVAILABLE, nullable=False)
    
    # Earnings and metrics
    total_earnings = Column(Float, default=0.0)
    daily_availability_hours = Column(Float, default=0.0)
    availability_start_time = Column(DateTime, nullable=True)
    
    # Cancellation tracking
    cancellation_count = Column(Integer, default=0)
    last_cancellation_reset = Column(DateTime, default=datetime.utcnow)
    
    # Extended area preferences (Requirements: 18.10, 18.11)
    accept_extended_area = Column(Boolean, default=True, nullable=False)
    accept_parcel_delivery = Column(Boolean, default=True, nullable=False)
    
    # Extended area statistics (Requirements: 18.12)
    extended_area_ride_count = Column(Integer, default=0)
    total_ride_count = Column(Integer, default=0)
    
    # Account flags
    is_suspended = Column(Boolean, default=False)
    is_flagged = Column(Boolean, default=False)
    
    # Relationships
    user = relationship("User", back_populates="driver_profile")
    
    def __repr__(self):
        return f"<DriverProfile(driver_id={self.driver_id}, status={self.status})>"


class EmergencyContact(Base):
    """Emergency contact information for users."""
    __tablename__ = "emergency_contacts"
    
    contact_id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.user_id"), nullable=False)
    
    name = Column(String(100), nullable=False)
    phone_number = Column(String(15), nullable=False)
    relationship_type = Column(String(50), nullable=False)  # Renamed from 'relationship'
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="emergency_contacts")
    
    def __repr__(self):
        return f"<EmergencyContact(name={self.name}, relationship={self.relationship_type})>"
