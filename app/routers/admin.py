"""
Pan-India Admin & Dispatcher Operations Router for RideConnect India.
Real-time fleet tracking, city-wise metrics, revenue dashboards, and driver KYC approvals.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from app.database import db
from app.services.india_geo import INDIAN_CITIES

router = APIRouter(prefix="/api/admin", tags=["Admin Operations"])


class UpdateDriverKYCRequest(BaseModel):
    driver_id: str
    status: str  # verified, rejected, pending
    rejection_reason: Optional[str] = None


class AdjustSurgeRequest(BaseModel):
    city_id: str
    surge_multiplier: float  # 1.0 to 3.0


@router.get("/metrics")
async def get_admin_metrics():
    """Pan-India KPI summary and operational status."""
    total_users = len(db.users)
    total_drivers = len(db.drivers)
    online_drivers = sum(1 for d in db.drivers.values() if d.get("is_online", False))
    total_rides = len(db.rides)
    completed_rides = sum(1 for r in db.rides.values() if r.get("status") == "completed")
    total_parcels = len(db.parcels)
    
    # Calculate revenue
    total_revenue_inr = sum(float(r.get("fare", 0.0)) for r in db.rides.values() if r.get("payment_status") == "paid")
    total_revenue_inr += sum(float(p.get("fare", 0.0)) for p in db.parcels.values() if p.get("payment_status") == "paid")
    platform_fee_inr = round(total_revenue_inr * 0.10, 2)

    # City-wise breakdown
    city_distribution = {}
    for d in db.drivers.values():
        c = d.get("city", "other").title()
        city_distribution[c] = city_distribution.get(c, 0) + 1

    return {
        "status": "healthy",
        "timestamp": "2026-10-26T21:00:00",
        "currency": "INR",
        "symbol": "₹",
        "kpis": {
            "total_users": total_users,
            "total_drivers": total_drivers,
            "online_drivers": online_drivers,
            "total_rides": total_rides,
            "completed_rides": completed_rides,
            "total_parcels": total_parcels,
            "gross_revenue": round(total_revenue_inr, 2),
            "platform_earnings": platform_fee_inr,
            "sos_alerts_active": len(db.emergency_alerts)
        },
        "city_driver_distribution": city_distribution,
        "supported_cities_count": len(INDIAN_CITIES)
    }


@router.get("/fleet")
async def get_live_fleet():
    """Retrieves live GPS positions of all drivers nationwide for the live map."""
    fleet = []
    for d in db.drivers.values():
        fleet.append({
            "id": d["id"],
            "name": d["name"],
            "city": d.get("city", "delhi").title(),
            "vehicle_type": d.get("vehicle_type", "sedan"),
            "vehicle_model": d.get("vehicle_model", "Dzire"),
            "plate_number": d.get("plate_number", "DL 01 AB 1234"),
            "is_online": d.get("is_online", False),
            "rating": d.get("rating", 4.9),
            "lat": d.get("lat", 28.6139),
            "lon": d.get("lon", 77.2090),
            "kyc_status": d.get("kyc_status", "verified")
        })
    return {
        "status": "success",
        "total": len(fleet),
        "fleet": fleet
    }


@router.get("/drivers-kyc")
async def get_drivers_kyc():
    """Lists all drivers pending or verified for KYC review."""
    return {
        "status": "success",
        "drivers": list(db.drivers.values())
    }


@router.put("/driver-kyc")
async def update_driver_kyc(req: UpdateDriverKYCRequest):
    """Approves or rejects driver documents and licenses."""
    driver = db.drivers.get(req.driver_id)
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found.")
        
    driver["kyc_status"] = req.status
    if req.rejection_reason:
        driver["kyc_rejection_reason"] = req.rejection_reason
        
    return {
        "status": "success",
        "message": f"Driver {driver['name']} KYC status updated to {req.status.upper()}."
    }
