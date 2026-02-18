"""
Tests for Transaction and DriverPayout models.
"""
import pytest
from datetime import datetime, timedelta
from app.models.transaction import (
    Transaction, DriverPayout, 
    TransactionStatus, PaymentGateway, PayoutStatus
)


class TestTransactionModel:
    """Test Transaction model."""
    
    def test_transaction_creation(self):
        """Test creating a transaction with all required fields."""
        transaction = Transaction(
            transaction_id="txn_123",
            ride_id="ride_123",
            rider_id="rider_123",
            driver_id="driver_123",
            amount=100.0,
            gateway=PaymentGateway.RAZORPAY,
            status=TransactionStatus.PENDING,
            retry_count=0,
            created_at=datetime.utcnow()
        )
        
        assert transaction.transaction_id == "txn_123"
        assert transaction.ride_id == "ride_123"
        assert transaction.amount == 100.0
        assert transaction.gateway == PaymentGateway.RAZORPAY
        assert transaction.status == TransactionStatus.PENDING
        assert transaction.retry_count == 0
    
    def test_transaction_with_gateway_fields(self):
        """Test transaction with gateway integration fields."""
        gateway_response = {
            "payment_id": "pay_xyz",
            "status": "captured",
            "method": "upi"
        }
        
        transaction = Transaction(
            transaction_id="txn_456",
            ride_id="ride_456",
            rider_id="rider_456",
            driver_id="driver_456",
            amount=150.0,
            gateway=PaymentGateway.PAYTM,
            status=TransactionStatus.SUCCESS,
            gateway_transaction_id="pay_xyz",
            gateway_response=gateway_response,
            retry_count=1,
            created_at=datetime.utcnow(),
            completed_at=datetime.utcnow()
        )
        
        assert transaction.gateway_transaction_id == "pay_xyz"
        assert transaction.gateway_response == gateway_response
        assert transaction.status == TransactionStatus.SUCCESS
        assert transaction.completed_at is not None
    
    def test_transaction_status_enum(self):
        """Test transaction status enumeration values."""
        assert TransactionStatus.PENDING.value == "pending"
        assert TransactionStatus.SUCCESS.value == "success"
        assert TransactionStatus.FAILED.value == "failed"
    
    def test_payment_gateway_enum(self):
        """Test payment gateway enumeration values."""
        assert PaymentGateway.RAZORPAY.value == "razorpay"
        assert PaymentGateway.PAYTM.value == "paytm"


class TestDriverPayoutModel:
    """Test DriverPayout model."""
    
    def test_payout_creation(self):
        """Test creating a driver payout with all required fields."""
        scheduled_time = datetime.utcnow() + timedelta(hours=24)
        rides = ["ride_1", "ride_2", "ride_3"]
        
        payout = DriverPayout(
            payout_id="payout_123",
            driver_id="driver_123",
            amount=500.0,
            rides=rides,
            status=PayoutStatus.SCHEDULED,
            bank_account="HDFC1234567890",
            scheduled_for=scheduled_time,
            created_at=datetime.utcnow()
        )
        
        assert payout.payout_id == "payout_123"
        assert payout.driver_id == "driver_123"
        assert payout.amount == 500.0
        assert payout.rides == rides
        assert payout.status == PayoutStatus.SCHEDULED
        assert payout.bank_account == "HDFC1234567890"
        assert payout.scheduled_for == scheduled_time
    
    def test_payout_with_gateway_fields(self):
        """Test payout with gateway integration fields."""
        gateway_response = {
            "transfer_id": "trans_abc",
            "status": "processed",
            "utr": "UTR123456"
        }
        
        payout = DriverPayout(
            payout_id="payout_456",
            driver_id="driver_456",
            amount=750.0,
            rides=["ride_4", "ride_5"],
            status=PayoutStatus.COMPLETED,
            bank_account="ICICI9876543210",
            gateway_payout_id="trans_abc",
            gateway_response=gateway_response,
            scheduled_for=datetime.utcnow(),
            processed_at=datetime.utcnow(),
            created_at=datetime.utcnow()
        )
        
        assert payout.gateway_payout_id == "trans_abc"
        assert payout.gateway_response == gateway_response
        assert payout.status == PayoutStatus.COMPLETED
        assert payout.processed_at is not None
    
    def test_payout_status_enum(self):
        """Test payout status enumeration values."""
        assert PayoutStatus.SCHEDULED.value == "scheduled"
        assert PayoutStatus.PROCESSING.value == "processing"
        assert PayoutStatus.COMPLETED.value == "completed"
        assert PayoutStatus.FAILED.value == "failed"
    
    def test_payout_multiple_rides(self):
        """Test payout can contain multiple ride IDs."""
        rides = [f"ride_{i}" for i in range(10)]
        
        payout = DriverPayout(
            payout_id="payout_789",
            driver_id="driver_789",
            amount=1200.0,
            rides=rides,
            status=PayoutStatus.SCHEDULED,
            bank_account="SBI1122334455",
            scheduled_for=datetime.utcnow() + timedelta(hours=24),
            created_at=datetime.utcnow()
        )
        
        assert len(payout.rides) == 10
        assert payout.rides[0] == "ride_0"
        assert payout.rides[9] == "ride_9"
