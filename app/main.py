"""
Main FastAPI Application Entry Point for RideConnect India.
Unified Ride-Hailing, Scheduled Rides, Courier Parcel Delivery, and Outstation Platform.
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import os

from app.config import settings
from app.routers import (
    auth,
    location,
    rides,
    scheduled_rides,
    parcels,
    drivers,
    payments,
    emergency,
    admin
)

app = FastAPI(
    title=settings.app_name,
    description="Pan-India Ride-Hailing, Scheduled Bookings, and P2P Parcel Delivery Platform",
    version="2.0.0"
)

# Cross-Origin Resource Sharing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(auth.router)
app.include_router(location.router)
app.include_router(rides.router)
app.include_router(scheduled_rides.router)
app.include_router(parcels.router)
app.include_router(drivers.router)
app.include_router(payments.router)
app.include_router(emergency.router)
app.include_router(admin.router)

# Mount static web directory
web_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "web")
if os.path.exists(web_dir):
    app.mount("/web", StaticFiles(directory=web_dir, html=True), name="web")


@app.get("/")
async def root():
    """Serves the main website homepage."""
    index_file = os.path.join(web_dir, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {
        "platform": settings.app_name,
        "version": "2.0.0",
        "documentation": "/docs",
        "web": "/web/"
    }


@app.get("/health")
async def health():
    """System health check endpoint."""
    return {
        "status": "healthy",
        "platform": "RideConnect India",
        "version": "2.0.0",
        "coverage": "All India (28 States & 8 Union Territories)",
        "services": {
            "instant_rides": "online",
            "scheduled_rides": "online",
            "parcel_courier": "online",
            "outstation": "online",
            "emergency_sos": "online",
            "upi_payments": "online"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
