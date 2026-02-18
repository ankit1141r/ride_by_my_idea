"""
Transaction and payment models for the ride-hailing platform.
Includes Transaction and DriverPayout models for payment processing.
"""
from sqlalchemy import Column, String, DateTime, Float, Integer, ForeignKey, Enum as SQLEnum, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.database import Base


class TransactionStatus(str, enum.Enum):
    """Transaction status enumeration."""
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"


class PaymentGateway(str, enum.Enum):
    """Payment gateway enumeration."""
    RAZORPAY = "razorpay"
    PAYTM = "paytm"


class PayoutStatus(str, enum.Enum):
    """Payout status enumeration."""
    SCHEDULED = "scheduled"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Transaction(Base):
    """Transaction model for payment records."""
    __tablename__ = "transactions"
    
    transaction_id = Column(String(100), primary_key=True)
    ride_id = Column(String(36), ForeignKey("rides.ride_id"), nullable=False, index=True)
    rider_id = Column(String(36), ForeignKey("users.user_id"), nullable=False, index=True)
    driver_id = Column(String(36), ForeignKey("users.user_id"), nullable=False, index=True)
    
    # Payment details
    amount = Column(Float, nullable=False)
    gateway = Column(SQLEnum(PaymentGateway), nullable=False)
    status = Column(SQLEnum(TransactionStatus), default=TransactionStatus.PENDING, nullable=False, index=True)
    
    # Gateway integration fields
    gateway_transaction_id = Column(String(100), nullable=True)
    gateway_response = Column(JSON, nullable=True)
    retry_count = Column(Integer, default=0, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    completed_at = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<Transaction(transaction_id={self.transaction_id}, ride_id={self.ride_id}, status={self.status}, amount={self.amount})>"


class DriverPayout(Base):
    """Driver payout model for payout scheduling and processing."""
    __tablename__ = "driver_payouts"
    
    payout_id = Column(String(100), primary_key=True)
    driver_id = Column(String(36), ForeignKey("users.user_id"), nullable=False, index=True)
    
    # Payout details
    amount = Column(Float, nullable=False)
    rides = Column(JSON, nullable=False)  # Array of ride IDs
    status = Column(SQLEnum(PayoutStatus), default=PayoutStatus.SCHEDULED, nullable=False, index=True)
    
    # Bank account information
    bank_account = Column(String(100), nullable=False)
    
    # Gateway integration fields
    gateway_payout_id = Column(String(100), nullable=True)
    gateway_response = Column(JSON, nullable=True)
    
    # Timestamps
    scheduled_for = Column(DateTime, nullable=False, index=True)
    processed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<DriverPayout(payout_id={self.payout_id}, driver_id={self.driver_id}, status={self.status}, amount={self.amount})>"
