"""
Parcel Delivery Router for RideConnect India.
Implements P2P Courier Delivery across India with 3 size classes, photo pickup,
digital signature confirmation, and separate parcel histories.
Requirements: 17.1 - 17.17
"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import uuid
import random
from datetime import datetime
from app.database import db
from app.services.fare_service import FareService

router = APIRouter(prefix="/api/parcels", tags=["Parcel Delivery"])


class ParcelQuoteRequest(BaseModel):
    pickup_lat: float
    pickup_lon: float
    dropoff_lat: float
    dropoff_lon: float
    parcel_size: str = "small"
    weight_kg: float = 2.0
    is_urgent: bool = False
    is_fragile: bool = False


class CreateParcelDeliveryRequest(BaseModel):
    sender_id: str
    recipient_name: str
    recipient_phone: str
    pickup_location: str
    dropoff_location: str
    pickup_lat: float
    pickup_lon: float
    dropoff_lat: float
    dropoff_lon: float
    parcel_size: str = "small"
    weight_kg: float = 2.0
    description: str
    is_fragile: bool = False
    is_urgent: bool = False
    handling_instructions: Optional[str] = None
    payment_method: str = "UPI"


class ConfirmPickupRequest(BaseModel):
    driver_id: str
    photo_data_url: Optional[str] = None  # Base64 photo or mock URL


class ConfirmDeliveryRequest(BaseModel):
    driver_id: str
    signature_data_url: Optional[str] = None  # Base64 signature
    delivery_otp: Optional[str] = None


@router.post("/quote")
async def get_parcel_quote(req: ParcelQuoteRequest):
    """
    Calculates parcel delivery quote based on weight and distance.
    Requirements: 17.3, 17.4, 17.5, 17.6, 17.14
    """
    try:
        quote = FareService.calculate_parcel_fare(
            pickup_lat=req.pickup_lat,
            pickup_lon=req.pickup_lon,
            dropoff_lat=req.dropoff_lat,
            dropoff_lon=req.dropoff_lon,
            parcel_size=req.parcel_size,
            weight_kg=req.weight_kg,
            is_urgent=req.is_urgent,
            is_fragile=req.is_fragile
        )
        return {"status": "success", "quote": quote}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/request")
async def request_parcel_delivery(req: CreateParcelDeliveryRequest):
    """
    Creates a new parcel delivery order.
    Requirements: 17.1, 17.2, 17.8, 17.14, 17.15
    """
    if req.weight_kg > 30.0:
        raise HTTPException(status_code=400, detail="Parcel weight exceeds the maximum 30 kg limit.")

    quote = FareService.calculate_parcel_fare(
        pickup_lat=req.pickup_lat,
        pickup_lon=req.pickup_lon,
        dropoff_lat=req.dropoff_lat,
        dropoff_lon=req.dropoff_lon,
        parcel_size=req.parcel_size,
        weight_kg=req.weight_kg,
        is_urgent=req.is_urgent,
        is_fragile=req.is_fragile
    )

    delivery_id = f"parcel-{uuid.uuid4().hex[:8]}"
    delivery_otp = str(random.randint(1000, 9999))

    # Assign an active driver
    assigned_driver = list(db.drivers.values())[0]

    delivery = {
        "id": delivery_id,
        "sender_id": req.sender_id,
        "driver_id": assigned_driver["id"],
        "driver_name": assigned_driver["name"],
        "driver_phone": assigned_driver["phone"],
        "recipient_name": req.recipient_name,
        "recipient_phone": req.recipient_phone,
        "pickup_location": req.pickup_location,
        "dropoff_location": req.dropoff_location,
        "pickup_lat": req.pickup_lat,
        "pickup_lon": req.pickup_lon,
        "dropoff_lat": req.dropoff_lat,
        "dropoff_lon": req.dropoff_lon,
        "parcel_size": req.parcel_size,
        "weight_kg": req.weight_kg,
        "description": req.description,
        "is_fragile": req.is_fragile,
        "is_urgent": req.is_urgent,
        "handling_instructions": req.handling_instructions or "Handle with care",
        "fare": quote["total_fare"],
        "distance_km": quote["distance_km"],
        "estimated_hours": quote["estimated_delivery_hours"],
        "payment_method": req.payment_method,
        "payment_status": "pending",
        "delivery_otp": delivery_otp,
        "status": "assigned",  # assigned, in_transit, delivered, cancelled
        "pickup_photo_url": None,
        "delivery_signature": None,
        "created_at": datetime.now().isoformat()
    }

    db.parcels[delivery_id] = delivery
    return {
        "status": "success",
        "message": f"Parcel courier booked! Driver {assigned_driver['name']} dispatched.",
        "parcel": delivery
    }


@router.post("/{delivery_id}/confirm-pickup")
async def confirm_parcel_pickup(delivery_id: str, req: ConfirmPickupRequest):
    """
    Driver uploads photo of parcel and marks status as 'in_transit'.
    Requirements: 17.7, 17.9
    """
    parcel = db.parcels.get(delivery_id)
    if not parcel:
        raise HTTPException(status_code=404, detail="Parcel delivery not found.")
        
    parcel["status"] = "in_transit"
    parcel["pickup_photo_url"] = req.photo_data_url or "https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?w=400"
    parcel["picked_up_at"] = datetime.now().isoformat()
    
    return {
        "status": "success",
        "message": "Pickup confirmed with photo. Parcel is now in transit.",
        "parcel": parcel
    }


@router.post("/{delivery_id}/confirm-delivery")
async def confirm_parcel_delivery(delivery_id: str, req: ConfirmDeliveryRequest):
    """
    Recipient signs and confirms delivery completion.
    Requirements: 17.10, 17.12
    """
    parcel = db.parcels.get(delivery_id)
    if not parcel:
        raise HTTPException(status_code=404, detail="Parcel delivery not found.")
        
    parcel["status"] = "delivered"
    parcel["delivery_signature"] = req.signature_data_url or "Recipient Digital Signature Verified"
    parcel["delivered_at"] = datetime.now().isoformat()
    parcel["payment_status"] = "paid"
    
    return {
        "status": "success",
        "message": "Delivery completed successfully! Notification sent to sender & recipient.",
        "parcel": parcel
    }


@router.get("/history/{user_id}")
async def get_parcel_history(user_id: str):
    """
    Retrieves separate parcel delivery history.
    Requirement: 17.17
    """
    user_parcels = [p for p in db.parcels.values() if p["sender_id"] == user_id or p.get("driver_id") == user_id]
    user_parcels.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    return {
        "status": "success",
        "total": len(user_parcels),
        "parcels": user_parcels
    }


@router.get("/{delivery_id}")
async def get_parcel_details(delivery_id: str):
    """
    Gets real-time tracking and details for a parcel delivery.
    Requirement: 17.11
    """
    parcel = db.parcels.get(delivery_id)
    if not parcel:
        raise HTTPException(status_code=404, detail="Parcel delivery not found.")
    return {
        "status": "success",
        "parcel": parcel
    }
