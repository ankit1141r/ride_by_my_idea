"""
Location & Geospatial Routing Router for Pan-India.
Supplies city registries, landmarks, route polylines, and interstate corridors.
Requirements: 2.1, 13.1 - 13.5, 18.1 - 18.8
"""
from fastapi import APIRouter, Query
from typing import Optional, List, Dict, Any
from app.services.india_geo import (
    INDIAN_CITIES,
    INTERCITY_CORRIDORS,
    calculate_haversine_distance,
    generate_route_waypoints,
    search_places_in_india
)

router = APIRouter(prefix="/api/location", tags=["Location & Geospatial"])


@router.get("/cities")
async def list_cities():
    """Lists all operational cities across India with center coordinates & landmarks."""
    return {
        "status": "success",
        "total_cities": len(INDIAN_CITIES),
        "cities": list(INDIAN_CITIES.values())
    }


@router.get("/search")
async def search_locations(q: str = Query(..., min_length=2), city: Optional[str] = None):
    """Searches landmarks, railway stations, airports, and localities in India."""
    results = search_places_in_india(q, city_hint=city)
    return {
        "query": q,
        "results": results
    }


@router.get("/route")
async def get_route(
    pickup_lat: float,
    pickup_lon: float,
    dropoff_lat: float,
    dropoff_lon: float
):
    """Calculates route distance, estimated travel time, and polyline coordinates."""
    dist_km = calculate_haversine_distance(pickup_lat, pickup_lon, dropoff_lat, dropoff_lon)
    is_highway = dist_km > 50.0
    speed = 60.0 if is_highway else 25.0
    duration_min = max(5, int((dist_km / speed) * 60))
    waypoints = generate_route_waypoints(pickup_lat, pickup_lon, dropoff_lat, dropoff_lon)
    
    return {
        "distance_km": dist_km,
        "duration_minutes": duration_min,
        "is_outstation": is_highway,
        "waypoints": waypoints
    }


@router.get("/outstation-corridors")
async def get_outstation_corridors():
    """Retrieves high-demand intercity outstation routes in India with tolls & distances."""
    return {
        "status": "success",
        "corridors": INTERCITY_CORRIDORS
    }
