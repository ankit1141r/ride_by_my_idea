"""
Scheduled Ride model for the ride-hailing platform.
Handles rides scheduled in advance (up to 7 days).
"""
from sqlalchemy import Column, String, DateTime, Float, JSON, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.database import Base


class ScheduledRideStatus(str, enum.Enum):
    """Scheduled ride status enumeration."""
    SCHEDULED = "scheduled"
    MATCHING = "matching"
    MATCHED = "matched"
    DRIVER_ARRIVING = "driver_arriving"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_DRIVER_FOUND = "no_driver_found"


class ScheduledRide(Base):
    """
    Scheduled ride model for advance bookings.
    
    Requirements: 16.1, 16.2, 16.4
    """
    __tablename__ = "scheduled_rides"
    
    ride_id = Column(String(36), primary_key=True)
    rider_id = Column(String(36), nullable=False, index=True)
    driver_id = Column(String(36), nullable=True, index=True)
    
    # Locations (stored as JSON)
    pickup_location = Column(JSON, nullable=False)
    destination = Column(JSON, nullable=False)
    
    # Scheduling
    scheduled_pickup_time = Column(DateTime, nullable=False, index=True)
    
    # Fare
    estimated_fare = Column(Float, nullable=False)
    fare_breakdown = Column(JSON, nullable=False)
    final_fare = Column(Float, nullable=True)
    
    # Status
    status = Column(SQLEnum(ScheduledRideStatus), default=ScheduledRideStatus.SCHEDULED, nullable=False, index=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    modified_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    matched_at = Column(DateTime, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    cancelled_at = Column(DateTime, nullable=True)
    
    # Reminders
    reminder_sent = Column(Boolean, default=False, nullable=False)
    driver_reminder_sent = Column(Boolean, default=False, nullable=False)
    
    # Cancellation
    cancellation_reason = Column(String(500), nullable=True)
    cancellation_fee = Column(Float, nullable=True)
    cancelled_by = Column(String(36), nullable=True)
    
    # Payment
    payment_status = Column(String(20), default="pending")
    transaction_id = Column(String(100), nullable=True)
    
    def __repr__(self):
        return f"<ScheduledRide(ride_id={self.ride_id}, status={self.status}, scheduled_time={self.scheduled_pickup_time})>"
