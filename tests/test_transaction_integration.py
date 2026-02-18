"""
Integration tests for Transaction and DriverPayout models with database.
"""
import pytest
from datetime import datetime, timedelta
from app.models import Transaction, DriverPayout, TransactionStatus, PaymentGateway, PayoutStatus


class TestTransactionIntegration:
    """Integration tests for Transaction model with database."""
    
    def test_create_transaction_in_db(self, db_session):
        """Test creating and persisting a transaction in the database."""
        transaction = Transaction(
            transaction_id="txn_integration_1",
            ride_id="ride_123",
            rider_id="rider_123",
            driver_id="driver_123",
            amount=100.0,
            gateway=PaymentGateway.RAZORPAY,
            status=TransactionStatus.PENDING,
            retry_count=0,
            created_at=datetime.utcnow()
        )
        
        db_session.add(transaction)
        db_session.commit()
        
        # Query back from database
        retrieved = db_session.query(Transaction).filter_by(
            transaction_id="txn_integration_1"
        ).first()
        
        assert retrieved is not None
        assert retrieved.transaction_id == "txn_integration_1"
        assert retrieved.amount == 100.0
        assert retrieved.gateway == PaymentGateway.RAZORPAY
        assert retrieved.status == TransactionStatus.PENDING
    
    def test_update_transaction_status(self, db_session):
        """Test updating transaction status and completion time."""
        transaction = Transaction(
            transaction_id="txn_integration_2",
            ride_id="ride_456",
            rider_id="rider_456",
            driver_id="driver_456",
            amount=150.0,
            gateway=PaymentGateway.PAYTM,
            status=TransactionStatus.PENDING,
            retry_count=0,
            created_at=datetime.utcnow()
        )
        
        db_session.add(transaction)
        db_session.commit()
        
        # Update status
        transaction.status = TransactionStatus.SUCCESS
        transaction.completed_at = datetime.utcnow()
        transaction.gateway_transaction_id = "pay_xyz"
        db_session.commit()
        
        # Verify update
        retrieved = db_session.query(Transaction).filter_by(
            transaction_id="txn_integration_2"
        ).first()
        
        assert retrieved.status == TransactionStatus.SUCCESS
        assert retrieved.completed_at is not None
        assert retrieved.gateway_transaction_id == "pay_xyz"
    
    def test_query_transactions_by_status(self, db_session):
        """Test querying transactions by status."""
        # Create multiple transactions
        for i in range(3):
            transaction = Transaction(
                transaction_id=f"txn_query_{i}",
                ride_id=f"ride_{i}",
                rider_id=f"rider_{i}",
                driver_id=f"driver_{i}",
                amount=100.0 * (i + 1),
                gateway=PaymentGateway.RAZORPAY,
                status=TransactionStatus.SUCCESS if i % 2 == 0 else TransactionStatus.PENDING,
                retry_count=0,
                created_at=datetime.utcnow()
            )
            db_session.add(transaction)
        
        db_session.commit()
        
        # Query successful transactions
        successful = db_session.query(Transaction).filter_by(
            status=TransactionStatus.SUCCESS
        ).all()
        
        assert len(successful) == 2
        assert all(t.status == TransactionStatus.SUCCESS for t in successful)


class TestDriverPayoutIntegration:
    """Integration tests for DriverPayout model with database."""
    
    def test_create_payout_in_db(self, db_session):
        """Test creating and persisting a driver payout in the database."""
        scheduled_time = datetime.utcnow() + timedelta(hours=24)
        rides = ["ride_1", "ride_2", "ride_3"]
        
        payout = DriverPayout(
            payout_id="payout_integration_1",
            driver_id="driver_123",
            amount=500.0,
            rides=rides,
            status=PayoutStatus.SCHEDULED,
            bank_account="HDFC1234567890",
            scheduled_for=scheduled_time,
            created_at=datetime.utcnow()
        )
        
        db_session.add(payout)
        db_session.commit()
        
        # Query back from database
        retrieved = db_session.query(DriverPayout).filter_by(
            payout_id="payout_integration_1"
        ).first()
        
        assert retrieved is not None
        assert retrieved.payout_id == "payout_integration_1"
        assert retrieved.amount == 500.0
        assert retrieved.rides == rides
        assert retrieved.status == PayoutStatus.SCHEDULED
    
    def test_update_payout_status(self, db_session):
        """Test updating payout status to completed."""
        payout = DriverPayout(
            payout_id="payout_integration_2",
            driver_id="driver_456",
            amount=750.0,
            rides=["ride_4", "ride_5"],
            status=PayoutStatus.SCHEDULED,
            bank_account="ICICI9876543210",
            scheduled_for=datetime.utcnow(),
            created_at=datetime.utcnow()
        )
        
        db_session.add(payout)
        db_session.commit()
        
        # Update to processing
        payout.status = PayoutStatus.PROCESSING
        db_session.commit()
        
        # Update to completed
        payout.status = PayoutStatus.COMPLETED
        payout.processed_at = datetime.utcnow()
        payout.gateway_payout_id = "trans_abc"
        db_session.commit()
        
        # Verify update
        retrieved = db_session.query(DriverPayout).filter_by(
            payout_id="payout_integration_2"
        ).first()
        
        assert retrieved.status == PayoutStatus.COMPLETED
        assert retrieved.processed_at is not None
        assert retrieved.gateway_payout_id == "trans_abc"
    
    def test_query_payouts_by_driver(self, db_session):
        """Test querying payouts for a specific driver."""
        driver_id = "driver_query_test"
        
        # Create multiple payouts for the same driver
        for i in range(3):
            payout = DriverPayout(
                payout_id=f"payout_driver_{i}",
                driver_id=driver_id,
                amount=100.0 * (i + 1),
                rides=[f"ride_{i}"],
                status=PayoutStatus.SCHEDULED,
                bank_account="SBI1122334455",
                scheduled_for=datetime.utcnow() + timedelta(hours=24 * i),
                created_at=datetime.utcnow()
            )
            db_session.add(payout)
        
        db_session.commit()
        
        # Query payouts for driver
        driver_payouts = db_session.query(DriverPayout).filter_by(
            driver_id=driver_id
        ).all()
        
        assert len(driver_payouts) == 3
        assert all(p.driver_id == driver_id for p in driver_payouts)
