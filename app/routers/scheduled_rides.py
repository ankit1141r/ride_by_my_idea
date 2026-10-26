"""
Scheduled Rides Router for RideConnect India.
Implements advance ride booking up to 7 days ahead with modification & cancellation policies.
Requirements: 16.1 - 16.12
"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import uuid
from datetime import datetime, timedelta
from app.database import db
from app.services.fare_service import FareService
from app.config import settings

router = APIRouter(prefix="/api/scheduled-rides", tags=["Scheduled Rides"])


class CreateScheduledRideRequest(BaseModel):
    rider_id: str
    pickup_location: str
    dropoff_location: str
    pickup_lat: float
    pickup_lon: float
    dropoff_lat: float
    dropoff_lon: float
    scheduled_time: str  # ISO string or YYYY-MM-DD HH:MM
    vehicle_type: str = "sedan"
    notes: Optional[str] = None


class ModifyScheduledRideRequest(BaseModel):
    pickup_location: Optional[str] = None
    dropoff_location: Optional[str] = None
    scheduled_time: Optional[str] = None
    vehicle_type: Optional[str] = None
    notes: Optional[str] = None


@router.post("")
async def create_scheduled_ride(req: CreateScheduledRideRequest):
    """
    Schedules a ride up to 7 days in advance.
    Requirements: 16.1, 16.2, 16.3, 16.4
    """
    # Parse scheduled time
    try:
        sch_time = datetime.fromisoformat(req.scheduled_time.replace("Z", ""))
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid scheduled time format. Use ISO format.")
        
    now = datetime.now()
    if sch_time < now + timedelta(minutes=15):
        raise HTTPException(status_code=400, detail="Scheduled time must be at least 15 minutes in the future.")
        
    if sch_time > now + timedelta(days=7):
        raise HTTPException(status_code=400, detail="Rides can only be scheduled up to 7 days in advance.")

    quotes = FareService.calculate_ride_quotes(
        req.pickup_lat, req.pickup_lon, req.dropoff_lat, req.dropoff_lon
    )
    quote = quotes["quotes"].get(req.vehicle_type, list(quotes["quotes"].values())[0])

    sched_id = f"sched-{uuid.uuid4().hex[:8]}"
    scheduled_ride = {
        "id": sched_id,
        "rider_id": req.rider_id,
        "pickup_location": req.pickup_location,
        "dropoff_location": req.dropoff_location,
        "pickup_lat": req.pickup_lat,
        "pickup_lon": req.pickup_lon,
        "dropoff_lat": req.dropoff_lat,
        "dropoff_lon": req.dropoff_lon,
        "scheduled_time": sch_time.isoformat(),
        "vehicle_type": req.vehicle_type,
        "estimated_fare": quote["total_fare"],
        "distance_km": quotes["distance_km"],
        "status": "scheduled",  # scheduled, matching, driver_assigned, completed, cancelled
        "notes": req.notes,
        "cancellation_fee": 0.0,
        "created_at": datetime.now().isoformat()
    }
    
    db.scheduled_rides[sched_id] = scheduled_ride
    return {
        "status": "success",
        "message": "Ride scheduled successfully!",
        "scheduled_ride": scheduled_ride
    }


@router.get("/user/{user_id}")
async def list_user_scheduled_rides(user_id: str):
    """
    Lists all scheduled rides for a user.
    Requirement: 16.12
    """
    rides = [r for r in db.scheduled_rides.values() if r["rider_id"] == user_id]
    rides.sort(key=lambda x: x["scheduled_time"])
    return {
        "status": "success",
        "total": len(rides),
        "scheduled_rides": rides
    }


@router.put("/{sched_id}")
async def modify_scheduled_ride(sched_id: str, req: ModifyScheduledRideRequest):
    """
    Allows riders to modify scheduled ride up to 2 hours before pickup.
    Requirement: 16.6
    """
    ride = db.scheduled_rides.get(sched_id)
    if not ride:
        raise HTTPException(status_code=404, detail="Scheduled ride not found.")
        
    sch_time = datetime.fromisoformat(ride["scheduled_time"])
    if datetime.now() > sch_time - timedelta(hours=2):
        raise HTTPException(
            status_code=400,
            detail="Modifications are only permitted up to 2 hours before scheduled pickup time."
        )

    if req.pickup_location:
        ride["pickup_location"] = req.pickup_location
    if req.dropoff_location:
        ride["dropoff_location"] = req.dropoff_location
    if req.vehicle_type:
        ride["vehicle_type"] = req.vehicle_type
    if req.notes is not None:
        ride["notes"] = req.notes
    if req.scheduled_time:
        ride["scheduled_time"] = req.scheduled_time
        
    return {
        "status": "success",
        "message": "Scheduled ride updated successfully.",
        "scheduled_ride": ride
    }


@router.delete("/{sched_id}")
async def cancel_scheduled_ride(sched_id: str):
    """
    Cancels a scheduled ride.
    Free if >1 hour before pickup; charges ₹30 fee if <1 hour before pickup.
    Requirements: 16.7, 16.8
    """
    ride = db.scheduled_rides.get(sched_id)
    if not ride:
        raise HTTPException(status_code=404, detail="Scheduled ride not found.")
        
    sch_time = datetime.fromisoformat(ride["scheduled_time"])
    hours_left = (sch_time - datetime.now()).total_seconds() / 3600.0
    
    fee = 0.0
    if hours_left < 1.0:
        fee = settings.scheduled_cancellation_fee  # ₹30 penalty
        
    ride["status"] = "cancelled"
    ride["cancellation_fee"] = fee
    ride["cancelled_at"] = datetime.now().isoformat()
    
    msg = "Scheduled ride cancelled without penalty." if fee == 0.0 else f"Cancelled within 1 hour. Cancellation fee of ₹{fee:.0f} applies."
    
    return {
        "status": "success",
        "message": msg,
        "cancellation_fee": fee,
        "scheduled_ride": ride
    }
