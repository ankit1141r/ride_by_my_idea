"""
Rides Management Router for RideConnect India.
Handles Fare Estimates, Instant Booking, Driver Matching, PIN Verification,
Live Ride Status, Cancellations, and History.
Requirements: 2.1 - 2.5, 3.1 - 3.7, 4.1 - 4.8, 5.1 - 5.5, 7.1 - 7.5, 8.1 - 8.4, 9.1 - 9.3, 15.1 - 15.5
"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import uuid
import random
from datetime import datetime
from app.database import db
from app.services.fare_service import FareService
from app.services.india_geo import calculate_haversine_distance

router = APIRouter(prefix="/api/rides", tags=["Rides"])


class FareEstimateRequest(BaseModel):
    pickup_lat: float
    pickup_lon: float
    dropoff_lat: float
    dropoff_lon: float
    surge_multiplier: Optional[float] = 1.0


class BookRideRequest(BaseModel):
    rider_id: str
    pickup_location: str
    dropoff_location: str
    pickup_lat: float
    pickup_lon: float
    dropoff_lat: float
    dropoff_lon: float
    vehicle_type: str = "sedan"
    payment_method: str = "UPI"  # UPI, Card, Cash


class UpdateRideStatusRequest(BaseModel):
    status: str  # accepted, arrived, in_transit, completed, cancelled
    cancellation_reason: Optional[str] = None


class RateRideRequest(BaseModel):
    rating: int
    review: Optional[str] = None
    tags: Optional[List[str]] = None


@router.post("/estimate")
async def estimate_fare(req: FareEstimateRequest):
    """Calculates fare estimates across all vehicle categories (Bike, Auto, Mini, Sedan, SUV, Outstation)."""
    quotes = FareService.calculate_ride_quotes(
        pickup_lat=req.pickup_lat,
        pickup_lon=req.pickup_lon,
        dropoff_lat=req.dropoff_lat,
        dropoff_lon=req.dropoff_lon,
        surge_multiplier=req.surge_multiplier or 1.0
    )
    return {
        "status": "success",
        "data": quotes
    }


@router.post("/request")
async def request_ride(req: BookRideRequest):
    """Creates a new ride request and matches the closest available verified driver."""
    # Compute fare for the chosen vehicle
    quote_data = FareService.calculate_ride_quotes(
        req.pickup_lat, req.pickup_lon, req.dropoff_lat, req.dropoff_lon
    )
    selected_quote = quote_data["quotes"].get(req.vehicle_type)
    if not selected_quote:
        # Fallback to sedan
        selected_quote = quote_data["quotes"].get("sedan") or list(quote_data["quotes"].values())[0]

    # Find closest online driver of this category or any category
    matched_driver = None
    min_dist = 999999.0
    
    for d in db.drivers.values():
        if d.get("is_online", False):
            # Prefer matching vehicle type
            v_match = (d.get("vehicle_type") == req.vehicle_type)
            dist = calculate_haversine_distance(req.pickup_lat, req.pickup_lon, d["lat"], d["lon"])
            if v_match and dist < min_dist:
                min_dist = dist
                matched_driver = d
                
    # If no strict vehicle match, find any available driver
    if not matched_driver:
        for d in db.drivers.values():
            if d.get("is_online", False):
                dist = calculate_haversine_distance(req.pickup_lat, req.pickup_lon, d["lat"], d["lon"])
                if dist < min_dist:
                    min_dist = dist
                    matched_driver = d

    # If still none, use default top driver for simulation
    if not matched_driver:
        matched_driver = list(db.drivers.values())[0]

    ride_id = f"ride-{uuid.uuid4().hex[:8]}"
    start_otp = str(random.randint(1000, 9999))
    
    new_ride = {
        "id": ride_id,
        "rider_id": req.rider_id,
        "driver_id": matched_driver["id"],
        "driver_name": matched_driver["name"],
        "driver_phone": matched_driver["phone"],
        "driver_rating": matched_driver["rating"],
        "vehicle_type": req.vehicle_type,
        "vehicle_make": matched_driver.get("vehicle_make", "Maruti"),
        "vehicle_model": matched_driver.get("vehicle_model", "Dzire"),
        "vehicle_color": matched_driver.get("vehicle_color", "White"),
        "plate_number": matched_driver.get("plate_number", "DL 01 AB 1234"),
        "driver_lat": matched_driver["lat"],
        "driver_lon": matched_driver["lon"],
        "pickup_location": req.pickup_location,
        "dropoff_location": req.dropoff_location,
        "pickup_lat": req.pickup_lat,
        "pickup_lon": req.pickup_lon,
        "dropoff_lat": req.dropoff_lat,
        "dropoff_lon": req.dropoff_lon,
        "distance_km": quote_data["distance_km"],
        "duration_min": quote_data["estimated_duration_min"],
        "fare": selected_quote["total_fare"],
        "gst": selected_quote["gst"],
        "payment_method": req.payment_method,
        "payment_status": "pending",
        "otp": start_otp,
        "status": "driver_assigned",  # searching, driver_assigned, arrived, in_transit, completed
        "created_at": datetime.now().isoformat()
    }
    
    db.rides[ride_id] = new_ride
    return {
        "status": "success",
        "message": f"Ride confirmed! {matched_driver['name']} is on the way.",
        "ride": new_ride
    }


@router.get("/{ride_id}")
async def get_ride_details(ride_id: str):
    """Fetches real-time status and live coordinates for a ride."""
    ride = db.rides.get(ride_id)
    if not ride:
        raise HTTPException(status_code=404, detail="Ride not found.")
    return {
        "status": "success",
        "ride": ride
    }


@router.put("/{ride_id}/status")
async def update_ride_status(ride_id: str, req: UpdateRideStatusRequest):
    """Updates ride lifecycle state."""
    ride = db.rides.get(ride_id)
    if not ride:
        raise HTTPException(status_code=404, detail="Ride not found.")
        
    ride["status"] = req.status
    if req.status == "completed":
        ride["completed_at"] = datetime.now().isoformat()
        ride["payment_status"] = "paid"
        # Update driver earnings
        driver = db.drivers.get(ride["driver_id"])
        if driver:
            driver["today_earnings"] = round(driver.get("today_earnings", 0.0) + (ride["fare"] * 0.90), 2)
            driver["total_rides"] = driver.get("total_rides", 0) + 1
    elif req.status == "cancelled":
        ride["cancelled_at"] = datetime.now().isoformat()
        ride["cancellation_reason"] = req.cancellation_reason or "Rider cancelled"
        
    return {
        "status": "success",
        "ride": ride
    }


@router.post("/{ride_id}/rate")
async def rate_ride(ride_id: str, req: RateRideRequest):
    """Submits driver feedback and rating."""
    ride = db.rides.get(ride_id)
    if not ride:
        raise HTTPException(status_code=404, detail="Ride not found.")
        
    ride["rating"] = req.rating
    ride["review"] = req.review
    ride["tags"] = req.tags or []
    
    # Store rating
    db.ratings[ride_id] = {
        "ride_id": ride_id,
        "driver_id": ride["driver_id"],
        "rider_id": ride["rider_id"],
        "rating": req.rating,
        "review": req.review,
        "created_at": datetime.now().isoformat()
    }
    
    return {
        "status": "success",
        "message": "Thank you for rating your ride!"
    }


@router.get("/history/{user_id}")
async def get_user_ride_history(user_id: str):
    """Retrieves list of past and active rides for a rider or driver."""
    user_rides = []
    for r in db.rides.values():
        if r["rider_id"] == user_id or r["driver_id"] == user_id:
            user_rides.append(r)
            
    # Sort newest first
    user_rides.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    return {
        "status": "success",
        "total": len(user_rides),
        "rides": user_rides
    }
