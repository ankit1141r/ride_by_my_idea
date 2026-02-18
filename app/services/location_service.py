"""
Location Service for managing driver locations and geospatial queries.
Handles MongoDB operations for location tracking.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import math
import googlemaps
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection
from pymongo import GEOSPHERE, ASCENDING, DESCENDING
from pymongo.errors import CollectionInvalid

from app.models.location import (
    Location, 
    LocationHistory,
    LOCATIONS_COLLECTION,
    LOCATION_HISTORY_COLLECTION,
    LOCATION_INDEXES,
    LOCATION_HISTORY_INDEXES
)
from app.config import settings


def calculate_distance(
    lat1: float, 
    lon1: float, 
    lat2: float, 
    lon2: float
) -> float:
    """
    Calculate the distance between two points using the Haversine formula.
    Returns distance in kilometers.
    
    Standalone function for use outside LocationService class.
    
    Args:
        lat1: Latitude of first point in degrees
        lon1: Longitude of first point in degrees
        lat2: Latitude of second point in degrees
        lon2: Longitude of second point in degrees
        
    Returns:
        Distance in kilometers
    """
    # Earth's radius in kilometers
    R = 6371.0
    
    # Convert degrees to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    # Differences
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    # Haversine formula
    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    # Distance in kilometers
    distance = R * c
    
    return distance


class LocationService:
    """
    Service for managing location data in MongoDB.
    Provides methods for storing and querying driver locations.
    
    Requirements: 2.1, 8.1, 8.2, 13.5, 18.1, 18.2
    """
    
    # Indore city center coordinates (Requirements: 18.1)
    CITY_CENTER_LAT = 22.7196
    CITY_CENTER_LON = 75.8577
    
    # Service area: 20km radius from city center (Requirements: 18.1)
    SERVICE_AREA_RADIUS_KM = 20.0
    
    # Original city limits (approximate rectangular bounds) (Requirements: 18.2)
    CITY_LIMITS = {
        "min_latitude": 22.6,
        "max_latitude": 22.8,
        "min_longitude": 75.7,
        "max_longitude": 75.9
    }
    
    # Legacy boundary for backward compatibility
    INDORE_BOUNDARY = CITY_LIMITS
    
    def __init__(self, db: AsyncIOMotorDatabase):
        """
        Initialize LocationService with MongoDB database.
        
        Args:
            db: AsyncIOMotorDatabase instance
        """
        self.db = db
        self.locations: AsyncIOMotorCollection = db[LOCATIONS_COLLECTION]
        self.location_history: AsyncIOMotorCollection = db[LOCATION_HISTORY_COLLECTION]
        
        # Initialize Google Maps client
        self.gmaps_client = None
        if settings.google_maps_api_key:
            self.gmaps_client = googlemaps.Client(key=settings.google_maps_api_key)
    
    async def initialize_indexes(self):
        """
        Create MongoDB indexes for geospatial queries and performance.
        Should be called once during application startup.
        """
        # Create indexes for locations collection
        for index_spec in LOCATION_INDEXES:
            await self.locations.create_index(
                index_spec["keys"],
                name=index_spec["name"],
                background=index_spec.get("background", True),
                unique=index_spec.get("unique", False),
                expireAfterSeconds=index_spec.get("expireAfterSeconds")
            )
        
        # Create indexes for location_history collection
        for index_spec in LOCATION_HISTORY_INDEXES:
            await self.location_history.create_index(
                index_spec["keys"],
                name=index_spec["name"],
                background=index_spec.get("background", True),
                unique=index_spec.get("unique", False)
            )
        
        print("MongoDB location indexes created successfully")
    
    def is_within_service_area(self, latitude: float, longitude: float) -> bool:
        """
        Check if a location is within the expanded service area (20km radius from city center).
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            
        Returns:
            True if location is within service area, False otherwise
            
        Requirements: 2.4, 13.6, 18.1, 18.2
        """
        distance_from_center = self.calculate_distance(
            self.CITY_CENTER_LAT,
            self.CITY_CENTER_LON,
            latitude,
            longitude
        )
        return distance_from_center <= self.SERVICE_AREA_RADIUS_KM
    
    def is_in_extended_area(self, latitude: float, longitude: float) -> bool:
        """
        Check if a location is in the extended area (beyond city limits but within 20km radius).
        
        Extended area is defined as locations that are:
        - Within the 20km service area radius, AND
        - Outside the original city limits
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            
        Returns:
            True if location is in extended area, False otherwise
            
        Requirements: 18.2, 18.3
        """
        # Check if within service area
        in_service_area = self.is_within_service_area(latitude, longitude)
        
        # Check if within city limits
        in_city_limits = (
            self.CITY_LIMITS["min_latitude"] <= latitude <= self.CITY_LIMITS["max_latitude"] and
            self.CITY_LIMITS["min_longitude"] <= longitude <= self.CITY_LIMITS["max_longitude"]
        )
        
        # Extended area = in service area but not in city limits
        return in_service_area and not in_city_limits
    
    def calculate_distance(
        self, 
        lat1: float, 
        lon1: float, 
        lat2: float, 
        lon2: float
    ) -> float:
        """
        Calculate the distance between two points using the Haversine formula.
        Returns distance in kilometers.
        
        The Haversine formula calculates the great-circle distance between two points
        on a sphere given their longitudes and latitudes.
        
        Args:
            lat1: Latitude of first point in degrees
            lon1: Longitude of first point in degrees
            lat2: Latitude of second point in degrees
            lon2: Longitude of second point in degrees
            
        Returns:
            Distance in kilometers
            
        Requirements: 5.1, 5.2
        """
        # Earth's radius in kilometers
        R = 6371.0
        
        # Convert degrees to radians
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)
        
        # Differences
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        # Haversine formula
        a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        # Distance in kilometers
        distance = R * c
        
        return distance
    
    def validate_location_boundaries(self, latitude: float, longitude: float) -> dict:
        """
        Validate if a location is within service boundaries and return detailed result.
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            
        Returns:
            Dictionary with validation result:
            {
                "valid": bool,
                "in_service_area": bool,
                "in_extended_area": bool,
                "distance_from_center_km": float,
                "message": str,
                "latitude": float,
                "longitude": float
            }
            
        Requirements: 2.4, 13.6, 18.1, 18.2, 18.3, 18.8
        """
        distance_from_center = self.calculate_distance(
            self.CITY_CENTER_LAT,
            self.CITY_CENTER_LON,
            latitude,
            longitude
        )
        
        is_valid = self.is_within_service_area(latitude, longitude)
        is_extended = self.is_in_extended_area(latitude, longitude)
        
        if is_valid:
            if is_extended:
                message = f"Location is in extended service area ({distance_from_center:.1f}km from city center). Extended area rides may have longer wait times."
            else:
                message = f"Location is within city center service area ({distance_from_center:.1f}km from city center)."
            
            return {
                "valid": True,
                "in_service_area": True,
                "in_extended_area": is_extended,
                "distance_from_center_km": distance_from_center,
                "message": message,
                "latitude": latitude,
                "longitude": longitude
            }
        else:
            return {
                "valid": False,
                "in_service_area": False,
                "in_extended_area": False,
                "distance_from_center_km": distance_from_center,
                "message": f"Location is outside service area. Service is only available within 20km of Indore city center. This location is {distance_from_center:.1f}km away.",
                "latitude": latitude,
                "longitude": longitude
            }
    
    async def update_driver_location(
        self, 
        driver_id: str, 
        latitude: float, 
        longitude: float,
        address: Optional[str] = None,
        status: Optional[str] = None,
        accuracy: Optional[float] = None
    ) -> Location:
        """
        Update driver's current location in MongoDB.
        
        Args:
            driver_id: Driver's user ID
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            address: Optional human-readable address
            status: Optional driver status (available, unavailable, busy)
            accuracy: Optional location accuracy in meters
            
        Returns:
            Location object that was stored
            
        Requirements: 4.4, 8.1, 8.2
        """
        location = Location.from_lat_lon(
            user_id=driver_id,
            user_type="driver",
            latitude=latitude,
            longitude=longitude,
            address=address,
            status=status,
            accuracy=accuracy,
            timestamp=datetime.utcnow()
        )
        
        # Insert location document
        await self.locations.insert_one(location.to_dict())
        
        return location
    
    async def get_driver_location(self, driver_id: str) -> Optional[Location]:
        """
        Get the most recent location for a driver.
        
        Args:
            driver_id: Driver's user ID
            
        Returns:
            Most recent Location object or None if not found
            
        Requirements: 8.1
        """
        doc = await self.locations.find_one(
            {"user_id": driver_id, "user_type": "driver"},
            sort=[("timestamp", DESCENDING)]
        )
        
        if doc:
            return Location(**doc)
        return None
    
    async def get_available_drivers_nearby(
        self, 
        latitude: float, 
        longitude: float, 
        radius_km: float = 5.0,
        limit: int = 50
    ) -> List[Location]:
        """
        Find available drivers within a radius of a location.
        Uses MongoDB geospatial query with 2dsphere index.
        
        Args:
            latitude: Center point latitude
            longitude: Center point longitude
            radius_km: Search radius in kilometers (default 5km)
            limit: Maximum number of drivers to return
            
        Returns:
            List of Location objects for available drivers, sorted by distance
            
        Requirements: 3.1, 4.3
        """
        # Convert km to meters for MongoDB query
        radius_meters = radius_km * 1000
        
        # Get the most recent location for each driver
        # First, get all recent driver locations within radius
        pipeline = [
            # Match locations within radius
            {
                "$geoNear": {
                    "near": {
                        "type": "Point",
                        "coordinates": [longitude, latitude]
                    },
                    "distanceField": "distance",
                    "maxDistance": radius_meters,
                    "query": {
                        "user_type": "driver",
                        "status": "available"
                    },
                    "spherical": True
                }
            },
            # Sort by timestamp descending to get most recent
            {"$sort": {"user_id": 1, "timestamp": -1}},
            # Group by user_id to get only the most recent location per driver
            {
                "$group": {
                    "_id": "$user_id",
                    "location": {"$first": "$$ROOT"}
                }
            },
            # Replace root with the location document
            {"$replaceRoot": {"newRoot": "$location"}},
            # Sort by distance
            {"$sort": {"distance": 1}},
            # Limit results
            {"$limit": limit}
        ]
        
        cursor = self.locations.aggregate(pipeline)
        locations = []
        
        async for doc in cursor:
            locations.append(Location(**doc))
        
        return locations
    
    async def start_location_history(
        self, 
        ride_id: str, 
        driver_id: str
    ) -> LocationHistory:
        """
        Start tracking location history for a ride.
        
        Args:
            ride_id: Ride ID
            driver_id: Driver ID
            
        Returns:
            LocationHistory object
            
        Requirements: 8.5
        """
        history = LocationHistory(
            ride_id=ride_id,
            driver_id=driver_id,
            started_at=datetime.utcnow()
        )
        
        await self.location_history.insert_one(history.to_dict())
        return history
    
    async def add_location_to_history(
        self, 
        ride_id: str, 
        location: Location
    ):
        """
        Add a location point to ride history.
        
        Args:
            ride_id: Ride ID
            location: Location object to add
            
        Requirements: 8.5
        """
        await self.location_history.update_one(
            {"ride_id": ride_id},
            {
                "$push": {"locations": location.to_dict()},
                "$set": {"ended_at": datetime.utcnow()}
            }
        )
    
    async def get_location_history(self, ride_id: str) -> Optional[LocationHistory]:
        """
        Get location history for a ride.
        
        Args:
            ride_id: Ride ID
            
        Returns:
            LocationHistory object or None if not found
            
        Requirements: 8.5, 9.5
        """
        doc = await self.location_history.find_one({"ride_id": ride_id})
        
        if doc:
            return LocationHistory(**doc)
        return None
    
    async def delete_old_locations(self, days: int = 1):
        """
        Delete location records older than specified days.
        Note: This is handled automatically by TTL index, but can be called manually.
        
        Args:
            days: Number of days to keep (default 1)
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        result = await self.locations.delete_many(
            {"timestamp": {"$lt": cutoff_date}}
        )
        return result.deleted_count
    
    def search_address(
        self, 
        query: str, 
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search for addresses using Google Maps Geocoding API.
        Filters results to only return locations within Indore service area.
        
        Args:
            query: Address search query string
            limit: Maximum number of results to return (default 5)
            
        Returns:
            List of address results with the following structure:
            [
                {
                    "address": str,  # Formatted address
                    "latitude": float,
                    "longitude": float,
                    "place_id": str  # Google Maps place ID
                }
            ]
            
        Requirements: 2.6, 13.5
        """
        if not self.gmaps_client:
            raise ValueError("Google Maps API key not configured")
        
        # Bias search results to Indore area
        # Center of Indore approximately
        indore_center = {
            "lat": (self.INDORE_BOUNDARY["min_latitude"] + self.INDORE_BOUNDARY["max_latitude"]) / 2,
            "lng": (self.INDORE_BOUNDARY["min_longitude"] + self.INDORE_BOUNDARY["max_longitude"]) / 2
        }
        
        # Add "Indore" to query if not already present
        if "indore" not in query.lower():
            query = f"{query}, Indore"
        
        try:
            # Call Google Maps Geocoding API
            geocode_result = self.gmaps_client.geocode(
                query,
                region="in",  # Bias to India
                bounds={
                    "northeast": {
                        "lat": self.INDORE_BOUNDARY["max_latitude"],
                        "lng": self.INDORE_BOUNDARY["max_longitude"]
                    },
                    "southwest": {
                        "lat": self.INDORE_BOUNDARY["min_latitude"],
                        "lng": self.INDORE_BOUNDARY["min_longitude"]
                    }
                }
            )
            
            # Filter results to only include locations within service area
            filtered_results = []
            for result in geocode_result[:limit * 2]:  # Get more results to filter
                location = result["geometry"]["location"]
                lat = location["lat"]
                lng = location["lng"]
                
                # Check if within service area
                if self.is_within_service_area(lat, lng):
                    filtered_results.append({
                        "address": result["formatted_address"],
                        "latitude": lat,
                        "longitude": lng,
                        "place_id": result["place_id"]
                    })
                    
                    if len(filtered_results) >= limit:
                        break
            
            return filtered_results
            
        except Exception as e:
            # Log error and return empty list
            print(f"Error searching address: {e}")
            return []
    
    def calculate_route(
        self,
        origin_lat: float,
        origin_lng: float,
        dest_lat: float,
        dest_lng: float
    ) -> Optional[Dict[str, Any]]:
        """
        Calculate route between two points using Google Maps Directions API.
        Returns route with polyline, distance, and duration.
        
        Args:
            origin_lat: Origin latitude
            origin_lng: Origin longitude
            dest_lat: Destination latitude
            dest_lng: Destination longitude
            
        Returns:
            Dictionary with route information:
            {
                "distance_km": float,  # Distance in kilometers
                "duration_minutes": int,  # Duration in minutes
                "polyline": str,  # Encoded polyline string
                "waypoints": List[Dict],  # List of waypoint coordinates
                "bounds": Dict  # Route bounding box
            }
            Returns None if route calculation fails.
            
        Requirements: 8.3, 8.6
        """
        if not self.gmaps_client:
            raise ValueError("Google Maps API key not configured")
        
        try:
            # Call Google Maps Directions API
            directions_result = self.gmaps_client.directions(
                origin=(origin_lat, origin_lng),
                destination=(dest_lat, dest_lng),
                mode="driving",
                departure_time="now",  # Get real-time traffic data
                traffic_model="best_guess"
            )
            
            if not directions_result:
                return None
            
            # Extract first route (best route)
            route = directions_result[0]
            leg = route["legs"][0]
            
            # Extract polyline
            polyline = route["overview_polyline"]["points"]
            
            # Extract distance and duration
            distance_meters = leg["distance"]["value"]
            distance_km = distance_meters / 1000.0
            
            duration_seconds = leg["duration"]["value"]
            duration_minutes = int(duration_seconds / 60)
            
            # Extract waypoints from steps
            waypoints = []
            for step in leg["steps"]:
                start_loc = step["start_location"]
                waypoints.append({
                    "latitude": start_loc["lat"],
                    "longitude": start_loc["lng"]
                })
            
            # Add final destination
            end_loc = leg["end_location"]
            waypoints.append({
                "latitude": end_loc["lat"],
                "longitude": end_loc["lng"]
            })
            
            # Extract bounds
            bounds = route["bounds"]
            
            return {
                "distance_km": round(distance_km, 2),
                "duration_minutes": duration_minutes,
                "polyline": polyline,
                "waypoints": waypoints,
                "bounds": {
                    "northeast": {
                        "latitude": bounds["northeast"]["lat"],
                        "longitude": bounds["northeast"]["lng"]
                    },
                    "southwest": {
                        "latitude": bounds["southwest"]["lat"],
                        "longitude": bounds["southwest"]["lng"]
                    }
                }
            }
            
        except Exception as e:
            # Log error and return None
            print(f"Error calculating route: {e}")
            return None
    
    def detect_route_deviation(
        self,
        current_lat: float,
        current_lng: float,
        route_waypoints: List[Dict[str, float]],
        threshold_meters: float = 500.0
    ) -> Dict[str, Any]:
        """
        Detect if current location deviates significantly from expected route.
        Calculates the minimum distance from current location to any point on the route.
        
        Args:
            current_lat: Current latitude
            current_lng: Current longitude
            route_waypoints: List of waypoint dictionaries with 'latitude' and 'longitude' keys
            threshold_meters: Deviation threshold in meters (default 500m)
            
        Returns:
            Dictionary with deviation information:
            {
                "is_deviated": bool,  # True if deviation exceeds threshold
                "deviation_distance_meters": float,  # Minimum distance to route in meters
                "current_location": Dict,  # Current location coordinates
                "closest_waypoint": Dict,  # Closest waypoint on route
                "threshold_meters": float  # Threshold used for detection
            }
            
        Requirements: 11.4
        """
        if not route_waypoints:
            return {
                "is_deviated": False,
                "deviation_distance_meters": 0.0,
                "current_location": {
                    "latitude": current_lat,
                    "longitude": current_lng
                },
                "closest_waypoint": None,
                "threshold_meters": threshold_meters
            }
        
        # Find minimum distance to any waypoint on the route
        min_distance_km = float('inf')
        closest_waypoint = None
        
        for waypoint in route_waypoints:
            waypoint_lat = waypoint.get("latitude")
            waypoint_lng = waypoint.get("longitude")
            
            if waypoint_lat is None or waypoint_lng is None:
                continue
            
            distance_km = self.calculate_distance(
                current_lat, current_lng,
                waypoint_lat, waypoint_lng
            )
            
            if distance_km < min_distance_km:
                min_distance_km = distance_km
                closest_waypoint = waypoint
        
        # Convert to meters
        deviation_distance_meters = min_distance_km * 1000.0
        
        # Check if deviation exceeds threshold
        is_deviated = deviation_distance_meters > threshold_meters
        
        return {
            "is_deviated": is_deviated,
            "deviation_distance_meters": round(deviation_distance_meters, 2),
            "current_location": {
                "latitude": current_lat,
                "longitude": current_lng
            },
            "closest_waypoint": closest_waypoint,
            "threshold_meters": threshold_meters
        }


# Helper function to get location service instance
def get_location_service(db: AsyncIOMotorDatabase) -> LocationService:
    """
    Get LocationService instance.
    
    Args:
        db: MongoDB database instance
        
    Returns:
        LocationService instance
    """
    return LocationService(db)
