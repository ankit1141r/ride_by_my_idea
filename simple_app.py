"""
Simple FastAPI application for demonstration.
This version runs without external dependencies.
"""
from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import os
import uuid
from datetime import datetime

app = FastAPI(
    title="RideConnect - Ride-Hailing Platform",
    description="A comprehensive ride-hailing platform",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for demo
users_db = {}
passwords_db = {}  # Store passwords separately for validation
rides_db = {}
drivers_available = {}

# Pydantic models
class UserRegister(BaseModel):
    name: str
    phone: str
    email: str
    password: str
    user_type: str = "rider"
    license_number: Optional[str] = None
    vehicle_registration: Optional[str] = None
    vehicle_make: Optional[str] = None
    vehicle_model: Optional[str] = None
    vehicle_color: Optional[str] = None

class UserLogin(BaseModel):
    phone: str
    password: str

class RideRequest(BaseModel):
    pickup_location: str
    dropoff_location: str
    pickup_lat: Optional[float] = 22.7196
    pickup_lon: Optional[float] = 75.8577
    dropoff_lat: Optional[float] = 22.7532
    dropoff_lon: Optional[float] = 75.8937

# Mount static files
if os.path.exists("web"):
    app.mount("/web", StaticFiles(directory="web"), name="web")

@app.get("/")
async def root():
    """Root endpoint - redirect to web interface."""
    return {"message": "RideConnect API", "docs": "/docs", "web": "/web/"}

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "message": "RideConnect is running",
        "version": "1.0.0"
    }

@app.get("/metrics")
async def get_metrics():
    """Get platform metrics."""
    return {
        "total_users": len(users_db),
        "total_rides": len(rides_db),
        "active_rides": sum(1 for r in rides_db.values() if r.get("status") == "in_progress"),
        "completed_rides": sum(1 for r in rides_db.values() if r.get("status") == "completed")
    }

# Authentication endpoints
@app.post("/api/auth/register")
async def register_user(user: UserRegister):
    """Register a new user."""
    # Check if user already exists
    if user.phone in users_db:
        raise HTTPException(status_code=400, detail="User already exists")
    
    # Validate password length
    if len(user.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
    
    # Create user
    user_id = str(uuid.uuid4())
    user_data = {
        "id": user_id,
        "name": user.name,
        "phone": user.phone,
        "email": user.email,
        "user_type": user.user_type,
        "created_at": datetime.now().isoformat(),
        "rating": 5.0
    }
    
    if user.user_type == "driver":
        user_data.update({
            "license_number": user.license_number,
            "vehicle_registration": user.vehicle_registration,
            "vehicle_make": user.vehicle_make,
            "vehicle_model": user.vehicle_model,
            "vehicle_color": user.vehicle_color,
            "is_available": False
        })
    
    users_db[user.phone] = user_data
    passwords_db[user.phone] = user.password  # Store password for validation
    
    # Generate token (simplified)
    token = f"token_{user_id}"
    
    return {
        "message": "User registered successfully",
        "user": user_data,
        "access_token": token,
        "token_type": "bearer"
    }

@app.post("/api/auth/login")
async def login_user(credentials: UserLogin):
    """Login user."""
    user = users_db.get(credentials.phone)
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Validate password
    stored_password = passwords_db.get(credentials.phone)
    if not stored_password or stored_password != credentials.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Generate token (simplified)
    token = f"token_{user['id']}"
    
    return {
        "message": "Login successful",
        "user": user,
        "access_token": token,
        "token_type": "bearer"
    }

# Ride endpoints
@app.post("/api/rides/request")
async def request_ride(ride: RideRequest):
    """Request a new ride."""
    ride_id = str(uuid.uuid4())
    
    # Calculate fare (simplified)
    distance = 5.2  # km
    fare = round(distance * 15 + 50)  # Base fare + per km
    
    ride_data = {
        "id": ride_id,
        "pickup_location": ride.pickup_location,
        "dropoff_location": ride.dropoff_location,
        "pickup_lat": ride.pickup_lat,
        "pickup_lon": ride.pickup_lon,
        "dropoff_lat": ride.dropoff_lat,
        "dropoff_lon": ride.dropoff_lon,
        "status": "pending",
        "fare": fare,
        "distance": distance,
        "created_at": datetime.now().isoformat()
    }
    
    rides_db[ride_id] = ride_data
    
    return {
        "message": "Ride requested successfully",
        "ride": ride_data
    }

@app.get("/api/rides/{ride_id}")
async def get_ride(ride_id: str):
    """Get ride details."""
    ride = rides_db.get(ride_id)
    
    if not ride:
        raise HTTPException(status_code=404, detail="Ride not found")
    
    return ride

@app.get("/api/rides/history")
async def get_ride_history():
    """Get ride history."""
    return {
        "rides": list(rides_db.values()),
        "total": len(rides_db)
    }

# Driver endpoints
@app.post("/api/drivers/availability")
async def update_driver_availability(request: Request):
    """Update driver availability."""
    data = await request.json()
    driver_id = data.get("driver_id", "demo_driver")
    is_available = data.get("is_available", False)
    
    drivers_available[driver_id] = {
        "is_available": is_available,
        "location": data.get("location", {"lat": 22.7196, "lon": 75.8577}),
        "updated_at": datetime.now().isoformat()
    }
    
    return {
        "message": "Availability updated",
        "is_available": is_available
    }

@app.get("/api/drivers/nearby")
async def get_nearby_drivers():
    """Get nearby available drivers."""
    available = [
        {
            "id": "driver_1",
            "name": "Priya Patel",
            "rating": 4.8,
            "vehicle": "Maruti Swift",
            "vehicle_number": "MP09AB1234",
            "distance": 1.2,
            "eta": 5
        },
        {
            "id": "driver_2",
            "name": "Rajesh Kumar",
            "rating": 4.9,
            "vehicle": "Honda City",
            "vehicle_number": "MP09CD5678",
            "distance": 2.1,
            "eta": 8
        }
    ]
    
    return {"drivers": available}

# Admin endpoints
@app.get("/api/admin/stats")
async def get_admin_stats():
    """Get admin statistics."""
    return {
        "total_users": len(users_db),
        "total_riders": sum(1 for u in users_db.values() if u.get("user_type") == "rider"),
        "total_drivers": sum(1 for u in users_db.values() if u.get("user_type") == "driver"),
        "total_rides": len(rides_db),
        "active_rides": sum(1 for r in rides_db.values() if r.get("status") == "in_progress"),
        "completed_rides": sum(1 for r in rides_db.values() if r.get("status") == "completed"),
        "total_revenue": sum(r.get("fare", 0) for r in rides_db.values() if r.get("status") == "completed")
    }

@app.get("/api/admin/users")
async def get_all_users():
    """Get all users."""
    return {"users": list(users_db.values())}

@app.get("/api/admin/rides")
async def get_all_rides():
    """Get all rides."""
    return {"rides": list(rides_db.values())}

@app.get("/web/", response_class=HTMLResponse)
async def serve_web_app():
    """Serve the main web application."""
    try:
        with open("web/index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Web interface not found")

# Sample API endpoints for demonstration
@app.get("/api/demo/users")
async def get_demo_users():
    """Demo endpoint showing sample users."""
    return {
        "users": [
            {"id": 1, "name": "Rahul Sharma", "type": "rider", "phone": "+919876543210"},
            {"id": 2, "name": "Priya Patel", "type": "driver", "phone": "+919876543211"},
            {"id": 3, "name": "Amit Kumar", "type": "rider", "phone": "+919876543212"}
        ]
    }

@app.get("/api/demo/rides")
async def get_demo_rides():
    """Demo endpoint showing sample rides."""
    return {
        "rides": [
            {
                "id": "ride_001",
                "rider": "Rahul Sharma",
                "driver": "Priya Patel",
                "pickup": "Rajwada, Indore",
                "dropoff": "Treasure Island Mall, Indore",
                "status": "completed",
                "fare": 120
            },
            {
                "id": "ride_002", 
                "rider": "Amit Kumar",
                "driver": "Priya Patel",
                "pickup": "Palasia Square, Indore",
                "dropoff": "Vijay Nagar, Indore",
                "status": "in_progress",
                "fare": 85
            }
        ]
    }

@app.get("/api/demo/stats")
async def get_demo_stats():
    """Demo endpoint showing platform statistics."""
    return {
        "total_users": 50,
        "total_drivers": 17,
        "total_rides": 200,
        "completed_rides": 180,
        "active_rides": 5,
        "total_revenue": 25000
    }

if __name__ == "__main__":
    import uvicorn
    import socket
    
    # Get local IP address
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    
    print("🚀 Starting RideConnect Demo Server")
    print("=" * 50)
    print("📱 Access from this computer:")
    print(f"   http://localhost:8001/web/")
    print(f"   http://127.0.0.1:8001/web/")
    print()
    print("📱 Access from mobile/other devices:")
    print(f"   http://192.168.1.3:8001/web/")
    print(f"   http://{local_ip}:8001/web/")
    print()
    print("📚 API Documentation:")
    print(f"   http://192.168.1.3:8001/docs")
    print()
    print("🔍 Health Check:")
    print(f"   http://192.168.1.3:8001/health")
    print("=" * 50)
    print("💡 Make sure your mobile is on the same WiFi network!")
    print()
    
    uvicorn.run(app, host="0.0.0.0", port=8001)