"""
Payment Service for processing payments through multiple gateways.
Handles payment processing, retries, and driver payouts.
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from enum import Enum
import uuid
import razorpay
from sqlalchemy.orm import Session
import logging

from app.config import settings
from app.models.transaction import Transaction, DriverPayout, TransactionStatus, PayoutStatus
from app.models.ride import Ride, RideStatus
from app.models.user import User, DriverProfile
from app.utils.circuit_breaker import CircuitBreaker, CircuitBreakerError

logger = logging.getLogger(__name__)


class PaymentGateway(str, Enum):
    """Supported payment gateways."""
    RAZORPAY = "razorpay"
    PAYTM = "paytm"


# Circuit breakers for payment gateways
razorpay_circuit_breaker = CircuitBreaker(
    failure_threshold=5,
    recovery_timeout=60,
    expected_exception=Exception
)

paytm_circuit_breaker = CircuitBreaker(
    failure_threshold=5,
    recovery_timeout=60,
    expected_exception=Exception
)


class PaymentGatewayInterface(ABC):
    """Abstract interface for payment gateway implementations."""
    
    @abstractmethod
    async def create_payment(
        self,
        amount: float,
        currency: str,
        order_id: str,
        customer_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create a payment transaction.
        
        Args:
            amount: Payment amount in rupees
            currency: Currency code (INR)
            order_id: Unique order identifier
            customer_info: Customer details (name, email, phone)
            
        Returns:
            Dict containing payment details and gateway response
        """
        pass
    
    @abstractmethod
    async def verify_payment(
        self,
        payment_id: str,
        order_id: str,
        signature: str
    ) -> bool:
        """
        Verify payment signature/status.
        
        Args:
            payment_id: Gateway payment ID
            order_id: Order identifier
            signature: Payment signature for verification
            
        Returns:
            True if payment is verified, False otherwise
        """
        pass
    
    @abstractmethod
    async def refund_payment(
        self,
        payment_id: str,
        amount: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Refund a payment (full or partial).
        
        Args:
            payment_id: Gateway payment ID
            amount: Refund amount (None for full refund)
            
        Returns:
            Dict containing refund details
        """
        pass


class RazorpayGateway(PaymentGatewayInterface):
    """Razorpay payment gateway implementation."""
    
    def __init__(self):
        """Initialize Razorpay client."""
        self.client = razorpay.Client(
            auth=(settings.razorpay_key_id, settings.razorpay_key_secret)
        )
    
    async def create_payment(
        self,
        amount: float,
        currency: str,
        order_id: str,
        customer_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a Razorpay payment order with circuit breaker protection."""
        def _create_order():
            # Convert amount to paise (Razorpay uses smallest currency unit)
            amount_paise = int(amount * 100)
            
            order_data = {
                "amount": amount_paise,
                "currency": currency,
                "receipt": order_id,
                "notes": customer_info
            }
            
            order = self.client.order.create(data=order_data)
            
            return {
                "success": True,
                "gateway_order_id": order["id"],
                "amount": amount,
                "currency": currency,
                "status": order["status"],
                "created_at": order["created_at"]
            }
        
        try:
            return razorpay_circuit_breaker.call(_create_order)
        except CircuitBreakerError as e:
            logger.error(f"Razorpay circuit breaker open: {str(e)}")
            return {
                "success": False,
                "error": "Payment gateway temporarily unavailable"
            }
        except Exception as e:
            logger.error(f"Razorpay payment creation failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def verify_payment(
        self,
        payment_id: str,
        order_id: str,
        signature: str
    ) -> bool:
        """Verify Razorpay payment signature."""
        try:
            params_dict = {
                "razorpay_order_id": order_id,
                "razorpay_payment_id": payment_id,
                "razorpay_signature": signature
            }
            self.client.utility.verify_payment_signature(params_dict)
            return True
        except razorpay.errors.SignatureVerificationError:
            return False
    
    async def refund_payment(
        self,
        payment_id: str,
        amount: Optional[float] = None
    ) -> Dict[str, Any]:
        """Process refund through Razorpay."""
        try:
            refund_data = {}
            if amount is not None:
                refund_data["amount"] = int(amount * 100)  # Convert to paise
            
            refund = self.client.payment.refund(payment_id, refund_data)
            
            return {
                "success": True,
                "refund_id": refund["id"],
                "amount": refund["amount"] / 100,  # Convert back to rupees
                "status": refund["status"]
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


class PaytmGateway(PaymentGatewayInterface):
    """Paytm payment gateway implementation (stub for now)."""
    
    def __init__(self):
        """Initialize Paytm client."""
        self.merchant_id = settings.paytm_merchant_id
        self.merchant_key = settings.paytm_merchant_key
    
    async def create_payment(
        self,
        amount: float,
        currency: str,
        order_id: str,
        customer_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a Paytm payment transaction."""
        # Note: Paytm SDK implementation would go here
        # For now, returning a stub response
        return {
            "success": False,
            "error": "Paytm gateway not fully implemented"
        }
    
    async def verify_payment(
        self,
        payment_id: str,
        order_id: str,
        signature: str
    ) -> bool:
        """Verify Paytm payment."""
        # Stub implementation
        return False
    
    async def refund_payment(
        self,
        payment_id: str,
        amount: Optional[float] = None
    ) -> Dict[str, Any]:
        """Process refund through Paytm."""
        # Stub implementation
        return {
            "success": False,
            "error": "Paytm gateway not fully implemented"
        }


class PaymentService:
    """Service for managing payments and payouts."""
    
    def __init__(self, db: Session):
        """
        Initialize payment service.
        
        Args:
            db: Database session
        """
        self.db = db
        self.gateways = {
            PaymentGateway.RAZORPAY: RazorpayGateway(),
            PaymentGateway.PAYTM: PaytmGateway()
        }
    
    def _get_gateway(self, gateway: PaymentGateway) -> PaymentGatewayInterface:
        """Get payment gateway instance."""
        return self.gateways[gateway]

    
    async def process_payment(
        self,
        ride_id: str,
        amount: float,
        gateway: PaymentGateway = PaymentGateway.RAZORPAY,
        retry_count: int = 0
    ) -> Transaction:
        """
        Process payment for a completed ride with retry logic.
        
        Args:
            ride_id: Ride identifier
            amount: Payment amount in rupees
            gateway: Payment gateway to use
            retry_count: Current retry attempt (0-2)
            
        Returns:
            Transaction record
        """
        # Get ride details
        ride = self.db.query(Ride).filter(Ride.ride_id == ride_id).first()
        if not ride:
            raise ValueError(f"Ride {ride_id} not found")
        
        # Create transaction record
        transaction = Transaction(
            transaction_id=str(uuid.uuid4()),
            ride_id=ride_id,
            rider_id=ride.rider_id,
            driver_id=ride.driver_id,
            amount=amount,
            gateway=gateway.value,
            status=TransactionStatus.PENDING,
            retry_count=retry_count
        )
        self.db.add(transaction)
        self.db.commit()
        self.db.refresh(transaction)
        
        # Get gateway instance
        gateway_client = self._get_gateway(gateway)
        
        # Prepare customer info
        customer_info = {
            "rider_id": ride.rider_id,
            "ride_id": ride_id
        }
        
        try:
            # Attempt payment
            result = await gateway_client.create_payment(
                amount=amount,
                currency="INR",
                order_id=ride_id,
                customer_info=customer_info
            )
            
            if result.get("success"):
                # Payment successful
                transaction.status = TransactionStatus.SUCCESS
                transaction.gateway_transaction_id = result.get("gateway_order_id")
                transaction.gateway_response = result
                transaction.completed_at = datetime.utcnow()
                
                # Update ride payment status
                ride.payment_status = "completed"
                
                self.db.commit()
                self.db.refresh(transaction)
                
                # Schedule driver payout
                await self.schedule_driver_payout(
                    driver_id=ride.driver_id,
                    ride_id=ride_id,
                    amount=amount * 0.8  # Driver gets 80% of fare
                )
                
                return transaction
            else:
                # Payment failed
                raise Exception(result.get("error", "Payment failed"))
                
        except Exception as e:
            # Payment failed - implement retry logic
            if retry_count < 2:
                # Retry with exponential backoff
                import asyncio
                backoff_seconds = 2 ** retry_count  # 1s, 2s, 4s
                await asyncio.sleep(backoff_seconds)
                
                # Update transaction status
                transaction.status = TransactionStatus.FAILED
                transaction.gateway_response = {"error": str(e)}
                self.db.commit()
                
                # Retry payment
                return await self.process_payment(
                    ride_id=ride_id,
                    amount=amount,
                    gateway=gateway,
                    retry_count=retry_count + 1
                )
            else:
                # All retries exhausted
                transaction.status = TransactionStatus.FAILED
                transaction.gateway_response = {"error": str(e), "retries_exhausted": True}
                transaction.completed_at = datetime.utcnow()
                
                # Update ride payment status
                ride.payment_status = "failed"
                
                self.db.commit()
                self.db.refresh(transaction)
                
                return transaction
    
    async def retry_failed_payment(self, transaction_id: str) -> Transaction:
        """
        Retry a failed payment transaction.
        
        Args:
            transaction_id: Transaction identifier
            
        Returns:
            Updated transaction record
        """
        transaction = self.db.query(Transaction).filter(
            Transaction.transaction_id == transaction_id
        ).first()
        
        if not transaction:
            raise ValueError(f"Transaction {transaction_id} not found")
        
        if transaction.status != TransactionStatus.FAILED:
            raise ValueError("Can only retry failed transactions")
        
        # Reset retry count and process payment
        return await self.process_payment(
            ride_id=transaction.ride_id,
            amount=transaction.amount,
            gateway=PaymentGateway(transaction.gateway),
            retry_count=0
        )
    
    async def schedule_driver_payout(
        self,
        driver_id: str,
        ride_id: str,
        amount: float
    ) -> DriverPayout:
        """
        Schedule driver payout within 24 hours of ride completion.
        
        Args:
            driver_id: Driver identifier
            ride_id: Ride identifier
            amount: Payout amount in rupees
            
        Returns:
            DriverPayout record
        """
        # Get driver profile to retrieve bank account
        driver = self.db.query(User).filter(User.user_id == driver_id).first()
        if not driver or not driver.driver_profile:
            raise ValueError(f"Driver {driver_id} not found")
        
        # TODO: Add bank_account field to DriverProfile model
        # For now, using a placeholder
        bank_account = "PLACEHOLDER_BANK_ACCOUNT"
        
        # Schedule payout for 24 hours from now
        scheduled_for = datetime.utcnow() + timedelta(hours=24)
        
        payout = DriverPayout(
            payout_id=str(uuid.uuid4()),
            driver_id=driver_id,
            amount=amount,
            rides=[ride_id],
            status=PayoutStatus.SCHEDULED,
            scheduled_for=scheduled_for,
            bank_account=bank_account
        )
        
        self.db.add(payout)
        self.db.commit()
        self.db.refresh(payout)
        
        return payout
    
    async def process_scheduled_payouts(self) -> List[DriverPayout]:
        """
        Process all scheduled payouts that are due.
        This should be called by a background job.
        
        Returns:
            List of processed payout records
        """
        # Get all scheduled payouts that are due
        now = datetime.utcnow()
        due_payouts = self.db.query(DriverPayout).filter(
            DriverPayout.status == PayoutStatus.SCHEDULED,
            DriverPayout.scheduled_for <= now
        ).all()
        
        processed_payouts = []
        
        for payout in due_payouts:
            try:
                # Update status to processing
                payout.status = PayoutStatus.PROCESSING
                self.db.commit()
                
                # Here you would integrate with bank transfer API
                # For now, we'll mark as completed
                # In production, this would call actual payout API
                
                payout.status = PayoutStatus.COMPLETED
                payout.processed_at = datetime.utcnow()
                self.db.commit()
                
                processed_payouts.append(payout)
                
            except Exception as e:
                # Mark payout as failed
                payout.status = PayoutStatus.FAILED
                self.db.commit()
        
        return processed_payouts
    
    def get_transaction_history(
        self,
        user_id: str,
        user_type: str = "rider"
    ) -> List[Transaction]:
        """
        Get transaction history for a user.
        
        Args:
            user_id: User identifier
            user_type: "rider" or "driver"
            
        Returns:
            List of transactions
        """
        if user_type == "rider":
            transactions = self.db.query(Transaction).filter(
                Transaction.rider_id == user_id
            ).order_by(Transaction.created_at.desc()).all()
        else:
            transactions = self.db.query(Transaction).filter(
                Transaction.driver_id == user_id
            ).order_by(Transaction.created_at.desc()).all()
        
        return transactions
    
    def get_payout_history(self, driver_id: str) -> List[DriverPayout]:
        """
        Get payout history for a driver.
        
        Args:
            driver_id: Driver identifier
            
        Returns:
            List of payouts
        """
        payouts = self.db.query(DriverPayout).filter(
            DriverPayout.driver_id == driver_id
        ).order_by(DriverPayout.created_at.desc()).all()
        
        return payouts
