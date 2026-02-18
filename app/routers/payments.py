"""
Payment endpoints for processing payments and managing transactions.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel

from app.database import get_db
from app.services.payment_service import PaymentService, PaymentGateway
from app.utils.jwt import get_current_user
from app.models.transaction import Transaction, DriverPayout


router = APIRouter(prefix="/api/payments", tags=["payments"])


# Request/Response schemas
class ProcessPaymentRequest(BaseModel):
    """Request schema for processing payment."""
    ride_id: str
    amount: float
    gateway: str = "razorpay"


class ProcessPaymentResponse(BaseModel):
    """Response schema for payment processing."""
    transaction_id: str
    status: str
    amount: float
    gateway: str
    message: str


class RetryPaymentRequest(BaseModel):
    """Request schema for retrying failed payment."""
    transaction_id: str


class TransactionResponse(BaseModel):
    """Response schema for transaction details."""
    transaction_id: str
    ride_id: str
    amount: float
    gateway: str
    status: str
    created_at: str
    completed_at: str = None
    
    class Config:
        from_attributes = True


class PayoutResponse(BaseModel):
    """Response schema for payout details."""
    payout_id: str
    driver_id: str
    amount: float
    status: str
    scheduled_for: str
    processed_at: str = None
    
    class Config:
        from_attributes = True


@router.post("/process", response_model=ProcessPaymentResponse)
async def process_payment(
    request: ProcessPaymentRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Process payment for a completed ride.
    
    Args:
        request: Payment processing request
        current_user: Authenticated user
        db: Database session
        
    Returns:
        Payment processing result
    """
    # Validate gateway
    try:
        gateway = PaymentGateway(request.gateway)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid payment gateway: {request.gateway}"
        )
    
    # Create payment service
    payment_service = PaymentService(db)
    
    try:
        # Process payment
        transaction = await payment_service.process_payment(
            ride_id=request.ride_id,
            amount=request.amount,
            gateway=gateway
        )
        
        return ProcessPaymentResponse(
            transaction_id=transaction.transaction_id,
            status=transaction.status.value,
            amount=transaction.amount,
            gateway=transaction.gateway.value,
            message="Payment processed successfully" if transaction.status.value == "success" 
                   else "Payment failed after retries"
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Payment processing failed: {str(e)}"
        )


@router.post("/retry", response_model=ProcessPaymentResponse)
async def retry_payment(
    request: RetryPaymentRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retry a failed payment transaction.
    
    Args:
        request: Retry payment request
        current_user: Authenticated user
        db: Database session
        
    Returns:
        Payment retry result
    """
    payment_service = PaymentService(db)
    
    try:
        transaction = await payment_service.retry_failed_payment(
            transaction_id=request.transaction_id
        )
        
        return ProcessPaymentResponse(
            transaction_id=transaction.transaction_id,
            status=transaction.status.value,
            amount=transaction.amount,
            gateway=transaction.gateway.value,
            message="Payment retry successful" if transaction.status.value == "success"
                   else "Payment retry failed"
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Payment retry failed: {str(e)}"
        )


@router.get("/history", response_model=List[TransactionResponse])
async def get_payment_history(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get payment transaction history for the current user.
    
    Args:
        current_user: Authenticated user
        db: Database session
        
    Returns:
        List of transactions
    """
    payment_service = PaymentService(db)
    
    # Get transactions based on user type
    transactions = payment_service.get_transaction_history(
        user_id=current_user["user_id"],
        user_type=current_user["user_type"]
    )
    
    return [
        TransactionResponse(
            transaction_id=t.transaction_id,
            ride_id=t.ride_id,
            amount=t.amount,
            gateway=t.gateway.value,
            status=t.status.value,
            created_at=t.created_at.isoformat(),
            completed_at=t.completed_at.isoformat() if t.completed_at else None
        )
        for t in transactions
    ]


@router.get("/payouts", response_model=List[PayoutResponse])
async def get_payout_history(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get payout history for the current driver.
    Only accessible by drivers.
    
    Args:
        current_user: Authenticated user
        db: Database session
        
    Returns:
        List of payouts
    """
    # Verify user is a driver
    if current_user["user_type"] != "driver":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only drivers can access payout history"
        )
    
    payment_service = PaymentService(db)
    payouts = payment_service.get_payout_history(driver_id=current_user["user_id"])
    
    return [
        PayoutResponse(
            payout_id=p.payout_id,
            driver_id=p.driver_id,
            amount=p.amount,
            status=p.status.value,
            scheduled_for=p.scheduled_for.isoformat(),
            processed_at=p.processed_at.isoformat() if p.processed_at else None
        )
        for p in payouts
    ]
