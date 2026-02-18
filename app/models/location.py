"""
Location data model for MongoDB.
Stores driver locations and location history for geospatial queries.
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, validator


class Coordinates(BaseModel):
    """GeoJSON Point coordinates."""
    type: str = "Point"
    coordinates: List[float]  # [longitude, latitude]
    
    @validator('coordinates')
    def validate_coordinates(cls, v):
        """Validate coordinates format."""
        if len(v) != 2:
            raise ValueError('Coordinates must be [longitude, latitude]')
        lon, lat = v
        if not (-180 <= lon <= 180):
            raise ValueError(f'Longitude must be between -180 and 180, got {lon}')
        if not (-90 <= lat <= 90):
            raise ValueError(f'Latitude must be between -90 and 90, got {lat}')
        return v


class Location(BaseModel):
    """
    Location document for MongoDB.
    Stores location data with geospatial indexing support.
    
    Requirements: 2.1, 8.1, 13.5
    """
    # MongoDB document ID
    location_id: Optional[str] = Field(None, alias="_id")
    
    # User/Driver identification
    user_id: str = Field(..., description="User ID (typically driver ID)")
    user_type: str = Field(..., description="Type: 'driver' or 'rider'")
    
    # GeoJSON format for geospatial queries
    location: Coordinates = Field(..., description="GeoJSON Point with [longitude, latitude]")
    
    # Human-readable address
    address: Optional[str] = Field(None, description="Human-readable address")
    city: str = Field(default="Indore", description="City name")
    
    # Metadata
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When location was recorded")
    accuracy: Optional[float] = Field(None, description="Location accuracy in meters")
    
    # Status information (for drivers)
    status: Optional[str] = Field(None, description="Driver status: available, unavailable, busy")
    
    class Config:
        """Pydantic configuration."""
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "user_id": "driver123",
                "user_type": "driver",
                "location": {
                    "type": "Point",
                    "coordinates": [75.8577, 22.7196]  # [longitude, latitude] for Indore
                },
                "address": "Vijay Nagar, Indore, Madhya Pradesh",
                "city": "Indore",
                "timestamp": "2024-01-15T10:30:00Z",
                "accuracy": 10.5,
                "status": "available"
            }
        }
    
    @classmethod
    def from_lat_lon(cls, user_id: str, user_type: str, latitude: float, 
                     longitude: float, address: Optional[str] = None, 
                     status: Optional[str] = None, **kwargs):
        """
        Create Location from latitude and longitude.
        
        Args:
            user_id: User/Driver ID
            user_type: Type of user ('driver' or 'rider')
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            address: Optional human-readable address
            status: Optional driver status
            **kwargs: Additional fields
            
        Returns:
            Location instance
        """
        return cls(
            user_id=user_id,
            user_type=user_type,
            location=Coordinates(
                type="Point",
                coordinates=[longitude, latitude]
            ),
            address=address,
            status=status,
            **kwargs
        )
    
    def get_latitude(self) -> float:
        """Get latitude from coordinates."""
        return self.location.coordinates[1]
    
    def get_longitude(self) -> float:
        """Get longitude from coordinates."""
        return self.location.coordinates[0]
    
    def to_dict(self) -> dict:
        """Convert to dictionary for MongoDB insertion."""
        data = self.model_dump(by_alias=True, exclude_none=True)
        # Remove _id if None to let MongoDB generate it
        if data.get('_id') is None:
            data.pop('_id', None)
        return data


class LocationHistory(BaseModel):
    """
    Location history for tracking ride routes.
    Stores a sequence of locations for a specific ride.
    """
    # MongoDB document ID
    history_id: Optional[str] = Field(None, alias="_id")
    
    # Ride identification
    ride_id: str = Field(..., description="Ride ID this history belongs to")
    driver_id: str = Field(..., description="Driver ID")
    
    # Location points
    locations: List[Location] = Field(default_factory=list, description="Sequence of locations")
    
    # Metadata
    started_at: datetime = Field(default_factory=datetime.utcnow)
    ended_at: Optional[datetime] = None
    total_distance: Optional[float] = Field(None, description="Total distance in kilometers")
    
    class Config:
        """Pydantic configuration."""
        populate_by_name = True
    
    def add_location(self, location: Location):
        """Add a location point to the history."""
        self.locations.append(location)
    
    def to_dict(self) -> dict:
        """Convert to dictionary for MongoDB insertion."""
        data = self.model_dump(by_alias=True, exclude_none=True)
        # Remove _id if None to let MongoDB generate it
        if data.get('_id') is None:
            data.pop('_id', None)
        return data


# MongoDB collection names
LOCATIONS_COLLECTION = "locations"
LOCATION_HISTORY_COLLECTION = "location_history"


# MongoDB indexes to create
LOCATION_INDEXES = [
    {
        "keys": [("location", "2dsphere")],
        "name": "location_2dsphere_idx",
        "background": True
    },
    {
        "keys": [("user_id", 1), ("timestamp", -1)],
        "name": "user_timestamp_idx",
        "background": True
    },
    {
        "keys": [("user_type", 1), ("status", 1)],
        "name": "user_type_status_idx",
        "background": True
    },
    {
        "keys": [("timestamp", -1)],
        "name": "timestamp_idx",
        "background": True,
        "expireAfterSeconds": 86400  # Auto-delete after 24 hours
    }
]

LOCATION_HISTORY_INDEXES = [
    {
        "keys": [("ride_id", 1)],
        "name": "ride_id_idx",
        "unique": True,
        "background": True
    },
    {
        "keys": [("driver_id", 1), ("started_at", -1)],
        "name": "driver_started_idx",
        "background": True
    }
]
