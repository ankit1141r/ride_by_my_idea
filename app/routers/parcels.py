"""
Parcel Delivery API endpoints.
Handles parcel delivery requests with photo and signature confirmations.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import uuid

from app.database import get_db
from app.models.parcel_delivery import ParcelDelivery, ParcelStatus, ParcelSize
from app.models.user import User
from app.schemas.parcel_delivery import (
    ParcelDeliveryRequest,
    ParcelPickupConfirmation,
    ParcelDeliveryConfirmation,
    ParcelDeliveryResponse
)
from app.services.location_service import LocationService, get_location_service
from app.services.fare_service import calculate_parcel_fare, estimate_delivery_time


router = APIRouter(prefix="/api/parcels", tags=["parcels"])


@router.post("/request", response_model=ParcelDeliveryResponse, status_code=status.HTTP_201_CREATED)
async def request_parcel_delivery(
    request: ParcelDeliveryRequest,
    sender_id: str,
    db: Session = Depends(get_db),
    location_service: LocationService = Depends(get_location_service)
):
    """
    Request a parcel delivery.
    
    Requirements: 17.1, 17.2, 17.13, 17.14
    """
    # Verify sender exists and is verified
    sender = db.query(User).filter(User.user_id == sender_id).first()
    
    if not sender:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sender not found"
        )
    
    # Validate sender is verified (Requirements: 17.1)
    if not sender.is_phone_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only verified users can request parcel delivery"
        )
    
    # Validate weight limit (Requirements: 17.14)
    if request.weight_kg > 30:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Parcel weight cannot exceed 30kg"
        )
    
    # Validate pickup location is within service area
    pickup_validation = location_service.validate_location_boundaries(
        request.pickup_location.latitude,
        request.pickup_location.longitude
    )
    
    if not pickup_validation["valid"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=pickup_validation["message"]
        )
    
    # Validate delivery location is within service area
    delivery_validation = location_service.validate_location_boundaries(
        request.delivery_location.latitude,
        request.delivery_location.longitude
    )
    
    if not delivery_validation["valid"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=delivery_validation["message"]
        )
    
    # Calculate distance
    distance_km = location_service.calculate_distance(
        request.pickup_location.latitude,
        request.pickup_location.longitude,
        request.delivery_location.latitude,
        request.delivery_location.longitude
    )
    
    # Calculate fare (Requirements: 17.4, 17.5, 17.6)
    fare_calc = calculate_parcel_fare(distance_km, request.parcel_size)
    
    # Estimate delivery time (Requirements: 17.13)
    delivery_time_minutes = estimate_delivery_time(distance_km)
    estimated_delivery_time = datetime.utcnow() + timedelta(minutes=delivery_time_minutes)
    
    # Create parcel delivery
    delivery_id = f"parcel_{uuid.uuid4().hex[:12]}"
    
    parcel_delivery = ParcelDelivery(
        delivery_id=delivery_id,
        sender_id=sender_id,
        recipient_phone=request.recipient_phone,
        recipient_name=request.recipient_name,
        pickup_location={
            "latitude": request.pickup_location.latitude,
            "longitude": request.pickup_location.longitude,
            "address": request.pickup_location.address
        },
        delivery_location={
            "latitude": request.delivery_location.latitude,
            "longitude": request.delivery_location.longitude,
            "address": request.delivery_location.address
        },
        parcel_size=ParcelSize(request.parcel_size),
        weight_kg=request.weight_kg,
        description=request.description,
        special_instructions=request.special_instructions,
        is_fragile=request.is_fragile,
        is_urgent=request.is_urgent,
        estimated_fare=fare_calc.total_fare,
        fare_breakdown={
            "base": fare_calc.base_fare,
            "per_km": fare_calc.breakdown.per_km,
            "distance": distance_km,
            "size": request.parcel_size
        },
        estimated_delivery_time=estimated_delivery_time,
        status=ParcelStatus.REQUESTED,
        created_at=datetime.utcnow()
    )
    
    db.add(parcel_delivery)
    db.commit()
    db.refresh(parcel_delivery)
    
    return ParcelDeliveryResponse(
        delivery_id=parcel_delivery.delivery_id,
        sender_id=parcel_delivery.sender_id,
        recipient_phone=parcel_delivery.recipient_phone,
        recipient_name=parcel_delivery.recipient_name,
        driver_id=parcel_delivery.driver_id,
        pickup_location=parcel_delivery.pickup_location,
        delivery_location=parcel_delivery.delivery_location,
        parcel_size=parcel_delivery.parcel_size.value,
        weight_kg=parcel_delivery.weight_kg,
        description=parcel_delivery.description,
        special_instructions=parcel_delivery.special_instructions,
        is_fragile=parcel_delivery.is_fragile,
        is_urgent=parcel_delivery.is_urgent,
        estimated_fare=parcel_delivery.estimated_fare,
        fare_breakdown=parcel_delivery.fare_breakdown,
        final_fare=parcel_delivery.final_fare,
        status=parcel_delivery.status.value,
        created_at=parcel_delivery.created_at,
        matched_at=parcel_delivery.matched_at,
        picked_up_at=parcel_delivery.picked_up_at,
        delivered_at=parcel_delivery.delivered_at,
        estimated_delivery_time=parcel_delivery.estimated_delivery_time,
        payment_status=parcel_delivery.payment_status
    )


@router.post("/{delivery_id}/confirm-pickup")
async def confirm_parcel_pickup(
    delivery_id: str,
    confirmation: ParcelPickupConfirmation,
    driver_id: str,
    db: Session = Depends(get_db)
):
    """
    Confirm parcel pickup with photo and optional signature.
    
    Requirements: 17.7, 17.8, 17.9
    """
    # Get the parcel delivery
    parcel = db.query(ParcelDelivery).filter(
        ParcelDelivery.delivery_id == delivery_id,
        ParcelDelivery.driver_id == driver_id
    ).first()
    
    if not parcel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parcel delivery not found or not assigned to this driver"
        )
    
    # Check status
    if parcel.status != ParcelStatus.MATCHED and parcel.status != ParcelStatus.DRIVER_ARRIVING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot confirm pickup for parcel with status: {parcel.status.value}"
        )
    
    # Store pickup confirmation (Requirements: 17.7, 17.8)
    parcel.pickup_photo_url = confirmation.pickup_photo
    parcel.pickup_signature = confirmation.pickup_signature
    parcel.picked_up_at = datetime.utcnow()
    parcel.status = ParcelStatus.IN_TRANSIT
    
    db.commit()
    
    return {
        "status": "success",
        "message": "Parcel pickup confirmed",
        "delivery_id": delivery_id,
        "picked_up_at": parcel.picked_up_at.isoformat()
    }


@router.post("/{delivery_id}/confirm-delivery")
async def confirm_parcel_delivery(
    delivery_id: str,
    confirmation: ParcelDeliveryConfirmation,
    driver_id: str,
    db: Session = Depends(get_db)
):
    """
    Confirm parcel delivery with signature and optional photo.
    
    Requirements: 17.10, 17.12
    """
    # Get the parcel delivery
    parcel = db.query(ParcelDelivery).filter(
        ParcelDelivery.delivery_id == delivery_id,
        ParcelDelivery.driver_id == driver_id
    ).first()
    
    if not parcel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parcel delivery not found or not assigned to this driver"
        )
    
    # Check status
    if parcel.status != ParcelStatus.IN_TRANSIT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot confirm delivery for parcel with status: {parcel.status.value}"
        )
    
    # Store delivery confirmation (Requirements: 17.10)
    parcel.delivery_signature = confirmation.delivery_signature
    parcel.delivery_photo_url = confirmation.delivery_photo
    parcel.delivered_at = datetime.utcnow()
    parcel.status = ParcelStatus.DELIVERED
    parcel.final_fare = parcel.estimated_fare  # Use estimated fare as final
    
    db.commit()
    
    # Send completion notifications (Requirements: 17.12)
    try:
        from app.services.notification_service import NotificationService
        from app.database import get_redis
        
        notification_service = NotificationService(get_redis())
        
        # Notification to sender
        sender_message = (
            f"Your parcel has been delivered successfully! "
            f"Delivery ID: {delivery_id}. "
            f"Delivered at: {parcel.delivered_at.strftime('%I:%M %p')}. "
            f"Final fare: ₹{parcel.final_fare:.2f}"
        )
        notification_service.send_dual_notification(
            user_id=parcel.sender_id,
            message=sender_message,
            notification_type="parcel_delivered"
        )
        
        # Notification to recipient (via SMS to recipient phone)
        recipient_message = (
            f"Parcel delivered from {parcel.sender_id}. "
            f"Delivery ID: {delivery_id}. "
            f"Delivered at: {parcel.delivered_at.strftime('%I:%M %p')}."
        )
        notification_service.send_sms_notification(
            phone_number=parcel.recipient_phone,
            message=recipient_message
        )
    except Exception as e:
        # Log error but don't fail the delivery confirmation
        print(f"Error sending completion notifications: {str(e)}")
    
    # TODO: Trigger payment processing
    
    return {
        "status": "success",
        "message": "Parcel delivery confirmed",
        "delivery_id": delivery_id,
        "delivered_at": parcel.delivered_at.isoformat(),
        "final_fare": parcel.final_fare
    }


@router.get("/{delivery_id}/location")
async def get_parcel_location(
    delivery_id: str,
    db: Session = Depends(get_db),
    location_service: LocationService = Depends(get_location_service)
):
    """
    Get real-time location of parcel delivery.
    
    Requirements: 17.11
    """
    # Get the parcel delivery
    parcel = db.query(ParcelDelivery).filter(
        ParcelDelivery.delivery_id == delivery_id
    ).first()
    
    if not parcel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parcel delivery not found"
        )
    
    # Check if parcel is in transit
    if parcel.status not in [ParcelStatus.DRIVER_ARRIVING, ParcelStatus.PICKED_UP, ParcelStatus.IN_TRANSIT]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Parcel location tracking is only available for in-transit deliveries"
        )
    
    # Get driver location
    if not parcel.driver_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No driver assigned to this parcel"
        )
    
    driver_location = location_service.get_driver_location(parcel.driver_id)
    
    if not driver_location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Driver location not available"
        )
    
    return {
        "delivery_id": delivery_id,
        "status": parcel.status.value,
        "driver_location": driver_location,
        "estimated_delivery_time": parcel.estimated_delivery_time.isoformat() if parcel.estimated_delivery_time else None
    }


@router.get("/history")
async def get_parcel_history(
    user_id: str,
    role: str,  # "sender" or "recipient"
    db: Session = Depends(get_db)
):
    """
    Get parcel delivery history for a user.
    
    Requirements: 17.17
    """
    if role == "sender":
        parcels = db.query(ParcelDelivery).filter(
            ParcelDelivery.sender_id == user_id
        ).order_by(ParcelDelivery.created_at.desc()).all()
    elif role == "recipient":
        # For recipients, we'd need to match by phone number
        # This is a simplified version
        parcels = []
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role must be 'sender' or 'recipient'"
        )
    
    return [
        ParcelDeliveryResponse(
            delivery_id=parcel.delivery_id,
            sender_id=parcel.sender_id,
            recipient_phone=parcel.recipient_phone,
            recipient_name=parcel.recipient_name,
            driver_id=parcel.driver_id,
            pickup_location=parcel.pickup_location,
            delivery_location=parcel.delivery_location,
            parcel_size=parcel.parcel_size.value,
            weight_kg=parcel.weight_kg,
            description=parcel.description,
            special_instructions=parcel.special_instructions,
            is_fragile=parcel.is_fragile,
            is_urgent=parcel.is_urgent,
            estimated_fare=parcel.estimated_fare,
            fare_breakdown=parcel.fare_breakdown,
            final_fare=parcel.final_fare,
            status=parcel.status.value,
            created_at=parcel.created_at,
            matched_at=parcel.matched_at,
            picked_up_at=parcel.picked_up_at,
            delivered_at=parcel.delivered_at,
            estimated_delivery_time=parcel.estimated_delivery_time,
            payment_status=parcel.payment_status
        )
        for parcel in parcels
    ]


@router.get("/{delivery_id}", response_model=ParcelDeliveryResponse)
async def get_parcel_details(
    delivery_id: str,
    db: Session = Depends(get_db)
):
    """Get details of a specific parcel delivery."""
    parcel = db.query(ParcelDelivery).filter(
        ParcelDelivery.delivery_id == delivery_id
    ).first()
    
    if not parcel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parcel delivery not found"
        )
    
    return ParcelDeliveryResponse(
        delivery_id=parcel.delivery_id,
        sender_id=parcel.sender_id,
        recipient_phone=parcel.recipient_phone,
        recipient_name=parcel.recipient_name,
        driver_id=parcel.driver_id,
        pickup_location=parcel.pickup_location,
        delivery_location=parcel.delivery_location,
        parcel_size=parcel.parcel_size.value,
        weight_kg=parcel.weight_kg,
        description=parcel.description,
        special_instructions=parcel.special_instructions,
        is_fragile=parcel.is_fragile,
        is_urgent=parcel.is_urgent,
        estimated_fare=parcel.estimated_fare,
        fare_breakdown=parcel.fare_breakdown,
        final_fare=parcel.final_fare,
        status=parcel.status.value,
        created_at=parcel.created_at,
        matched_at=parcel.matched_at,
        picked_up_at=parcel.picked_up_at,
        delivered_at=parcel.delivered_at,
        estimated_delivery_time=parcel.estimated_delivery_time,
        payment_status=parcel.payment_status
    )
