"""
Ride models for the ride-hailing platform.
Includes Ride model with status tracking and related enums.
"""
from sqlalchemy import Column, String, DateTime, Float, Integer, ForeignKey, Enum as SQLEnum, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.database import Base


class RideStatus(str, enum.Enum):
    """Ride status enumeration with valid state transitions."""
    REQUESTED = "requested"
    MATCHED = "matched"
    DRIVER_ARRIVING = "driver_arriving"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class PaymentStatus(str, enum.Enum):
    """Payment status enumeration."""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"


class Ride(Base):
    """Ride model tracking the complete ride lifecycle."""
    __tablename__ = "rides"
    
    ride_id = Column(String(36), primary_key=True)
    rider_id = Column(String(36), ForeignKey("users.user_id"), nullable=False, index=True)
    driver_id = Column(String(36), ForeignKey("users.user_id"), nullable=True, index=True)
    status = Column(SQLEnum(RideStatus), default=RideStatus.REQUESTED, nullable=False, index=True)
    
    # Location information (stored as JSON with lat, lon, address)
    pickup_location = Column(JSON, nullable=False)
    destination = Column(JSON, nullable=False)
    actual_route = Column(JSON, nullable=True)
    
    # Timing information
    requested_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    matched_at = Column(DateTime, nullable=True)
    pickup_time = Column(DateTime, nullable=True)
    start_time = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Fare information
    estimated_fare = Column(Float, nullable=False)
    final_fare = Column(Float, nullable=True)
    fare_breakdown = Column(JSON, nullable=False)
    
    # Payment information
    payment_status = Column(SQLEnum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False)
    transaction_id = Column(String(100), nullable=True)
    
    # Rating information
    rider_rating = Column(Integer, nullable=True)
    rider_review = Column(String(500), nullable=True)
    rider_rating_timestamp = Column(DateTime, nullable=True)
    
    driver_rating = Column(Integer, nullable=True)
    driver_review = Column(String(500), nullable=True)
    driver_rating_timestamp = Column(DateTime, nullable=True)
    
    # Cancellation information
    cancelled_by = Column(String(36), nullable=True)
    cancellation_reason = Column(String(500), nullable=True)
    cancellation_fee = Column(Float, nullable=True)
    cancellation_timestamp = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<Ride(ride_id={self.ride_id}, status={self.status}, rider_id={self.rider_id}, driver_id={self.driver_id})>"
    
    def is_cancellable(self):
        """Check if the ride can be cancelled based on current status."""
        return self.status in [RideStatus.REQUESTED, RideStatus.MATCHED, RideStatus.DRIVER_ARRIVING]
    
    def can_transition_to(self, new_status):
        """
        Validate if transition to new status is allowed.
        
        Valid transitions:
        - REQUESTED -> MATCHED, CANCELLED
        - MATCHED -> DRIVER_ARRIVING, CANCELLED
        - DRIVER_ARRIVING -> IN_PROGRESS, CANCELLED
        - IN_PROGRESS -> COMPLETED
        - COMPLETED -> (no transitions)
        - CANCELLED -> (no transitions)
        """
        valid_transitions = {
            RideStatus.REQUESTED: [RideStatus.MATCHED, RideStatus.CANCELLED],
            RideStatus.MATCHED: [RideStatus.DRIVER_ARRIVING, RideStatus.CANCELLED],
            RideStatus.DRIVER_ARRIVING: [RideStatus.IN_PROGRESS, RideStatus.CANCELLED],
            RideStatus.IN_PROGRESS: [RideStatus.COMPLETED],
            RideStatus.COMPLETED: [],
            RideStatus.CANCELLED: []
        }
        
        return new_status in valid_transitions.get(self.status, [])
