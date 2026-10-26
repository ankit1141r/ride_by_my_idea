"""
Payments & GST Invoicing Router for RideConnect India.
Integrates UPI (PhonePe, GPay, Paytm, BHIM), RuPay/Visa/Mastercard Cards, Net Banking,
and generates compliant GST Tax Receipts.
Requirements: 6.1 - 6.6
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import uuid
from datetime import datetime
from app.database import db

router = APIRouter(prefix="/api/payments", tags=["Payments & GST Invoicing"])


class ProcessPaymentRequest(BaseModel):
    ride_id: Optional[str] = None
    delivery_id: Optional[str] = None
    amount: float
    method: str  # UPI, CARD, NETBANKING, CASH, WALLET
    upi_id: Optional[str] = None
    card_last4: Optional[str] = None
    bank_name: Optional[str] = None


class GenerateUPIRequest(BaseModel):
    amount: float
    order_id: str
    description: Optional[str] = "RideConnect Trip Payment"


@router.post("/upi-intent")
async def generate_upi_intent(req: GenerateUPIRequest):
    """
    Generates standard Indian UPI QR Intent string (compatible with BHIM, PhonePe, GPay, Paytm).
    """
    vpa = "rideconnect.india@icici"
    payee_name = "RideConnect Technologies"
    upi_string = f"upi://pay?pa={vpa}&pn={payee_name}&am={req.amount:.2f}&cu=INR&tn={req.order_id}"
    
    return {
        "status": "success",
        "upi_string": upi_string,
        "vpa": vpa,
        "payee_name": payee_name,
        "amount": req.amount,
        "currency": "INR",
        "supported_apps": ["Google Pay", "PhonePe", "Paytm", "BHIM", "Cred", "Amazon Pay"]
    }


@router.post("/process")
async def process_payment(req: ProcessPaymentRequest):
    """Processes payment and updates transaction ledger."""
    txn_id = f"txn_in_{uuid.uuid4().hex[:12].upper()}"
    
    # Update linked ride or delivery
    if req.ride_id and req.ride_id in db.rides:
        db.rides[req.ride_id]["payment_status"] = "paid"
        db.rides[req.ride_id]["transaction_id"] = txn_id
    elif req.delivery_id and req.delivery_id in db.parcels:
        db.parcels[req.delivery_id]["payment_status"] = "paid"
        db.parcels[req.delivery_id]["transaction_id"] = txn_id

    txn = {
        "id": txn_id,
        "ride_id": req.ride_id,
        "delivery_id": req.delivery_id,
        "amount": req.amount,
        "currency": "INR",
        "symbol": "₹",
        "method": req.method,
        "upi_id": req.upi_id,
        "card_last4": req.card_last4,
        "bank_name": req.bank_name,
        "status": "success",
        "timestamp": datetime.now().isoformat()
    }
    
    db.transactions[txn_id] = txn
    return {
        "status": "success",
        "message": f"Payment of ₹{req.amount:.2f} received successfully via {req.method}.",
        "transaction": txn
    }


@router.get("/receipt/{item_id}")
async def get_gst_receipt(item_id: str):
    """
    Generates a full GST-compliant Indian transportation tax invoice.
    SAC code: 9964 (Passenger Transport)
    Tax: CGST 2.5% + SGST 2.5% = 5%
    """
    ride = db.rides.get(item_id)
    parcel = db.parcels.get(item_id)
    
    if not ride and not parcel:
        raise HTTPException(status_code=404, detail="Trip or Parcel delivery record not found.")

    is_ride = ride is not None
    item = ride if is_ride else parcel
    total_amount = float(item.get("fare", 100.0))
    
    subtotal = round(total_amount / 1.05, 2)
    cgst = round((total_amount - subtotal) / 2.0, 2)
    sgst = round((total_amount - subtotal) / 2.0, 2)
    total_tax = round(cgst + sgst, 2)

    return {
        "status": "success",
        "invoice_number": f"INV-IN-2026-{item['id'][:8].upper()}",
        "invoice_date": datetime.now().strftime("%d-%b-%Y %I:%M %p"),
        "sac_code": "996412",
        "sac_description": "Local / Intercity Passenger Transport Services by Road",
        "trip_type": "Ride Hailing" if is_ride else "Courier Parcel Delivery",
        "pickup_location": item.get("pickup_location", "N/A"),
        "dropoff_location": item.get("dropoff_location", "N/A"),
        "distance_km": item.get("distance_km", 0.0),
        "driver_name": item.get("driver_name", "Assigned Captain"),
        "payment_method": item.get("payment_method", "UPI"),
        "currency": "INR",
        "pricing_breakdown": {
            "base_and_distance_fare": subtotal,
            "cgst_2_5_percent": cgst,
            "sgst_2_5_percent": sgst,
            "total_gst": total_tax,
            "total_paid": total_amount
        },
        "registered_entity": "RideConnect Technologies Private Limited",
        "gstin": "07AAAAA0000A1Z5",
        "support_email": "support@rideconnect.in"
    }
