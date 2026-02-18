"""
Parcel Delivery model for the ride-hailing platform.
Handles parcel delivery requests with photo and signature confirmations.
"""
from sqlalchemy import Column, String, DateTime, Float, JSON, Boolean, Enum as SQLEnum, Text
from datetime import datetime
import enum
from app.database import Base


class ParcelStatus(str, enum.Enum):
    """Parcel delivery status enumeration."""
    REQUESTED = "requested"
    MATCHED = "matched"
    DRIVER_ARRIVING = "driver_arriving"
    PICKED_UP = "picked_up"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class ParcelSize(str, enum.Enum):
    """Parcel size classification."""
    SMALL = "small"   # Up to 5kg
    MEDIUM = "medium" # 5-15kg
    LARGE = "large"   # 15-30kg


class ParcelDelivery(Base):
    """
    Parcel delivery model.
    
    Requirements: 17.2, 17.3
    """
    __tablename__ = "parcel_deliveries"
    
    delivery_id = Column(String(36), primary_key=True)
    sender_id = Column(String(36), nullable=False, index=True)
    recipient_phone = Column(String(15), nullable=False)
    recipient_name = Column(String(100), nullable=False)
    driver_id = Column(String(36), nullable=True, index=True)
    
    # Locations (stored as JSON)
    pickup_location = Column(JSON, nullable=False)
    delivery_location = Column(JSON, nullable=False)
    
    # Parcel details
    parcel_size = Column(SQLEnum(ParcelSize), nullable=False)
    weight_kg = Column(Float, nullable=False)
    description = Column(String(500), nullable=True)
    special_instructions = Column(Text, nullable=True)
    is_fragile = Column(Boolean, default=False, nullable=False)
    is_urgent = Column(Boolean, default=False, nullable=False)
    
    # Fare
    estimated_fare = Column(Float, nullable=False)
    fare_breakdown = Column(JSON, nullable=False)
    final_fare = Column(Float, nullable=True)
    
    # Status
    status = Column(SQLEnum(ParcelStatus), default=ParcelStatus.REQUESTED, nullable=False, index=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    matched_at = Column(DateTime, nullable=True)
    picked_up_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)
    cancelled_at = Column(DateTime, nullable=True)
    
    # Estimated delivery time
    estimated_delivery_time = Column(DateTime, nullable=True)
    
    # Confirmations
    pickup_photo_url = Column(String(500), nullable=True)
    pickup_signature = Column(Text, nullable=True)
    delivery_photo_url = Column(String(500), nullable=True)
    delivery_signature = Column(Text, nullable=True)
    
    # Cancellation
    cancellation_reason = Column(String(500), nullable=True)
    cancelled_by = Column(String(36), nullable=True)
    
    # Payment
    payment_status = Column(String(20), default="pending")
    transaction_id = Column(String(100), nullable=True)
    
    def __repr__(self):
        return f"<ParcelDelivery(delivery_id={self.delivery_id}, status={self.status}, size={self.parcel_size})>"
