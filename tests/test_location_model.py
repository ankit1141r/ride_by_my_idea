"""
Unit tests for Location data model.
Tests Requirements 2.1, 8.1, 13.5
"""
import pytest
from datetime import datetime

from app.models.location import Location, Coordinates, LocationHistory


class TestCoordinates:
    """Test Coordinates model validation."""
    
    def test_valid_coordinates(self):
        """Test that valid coordinates are accepted."""
        coords = Coordinates(
            type="Point",
            coordinates=[75.8577, 22.7196]  # Indore coordinates
        )
        assert coords.type == "Point"
        assert coords.coordinates == [75.8577, 22.7196]
    
    def test_invalid_longitude(self):
        """Test that invalid longitude is rejected."""
        with pytest.raises(ValueError, match="Longitude must be between"):
            Coordinates(
                type="Point",
                coordinates=[200.0, 22.7196]  # Invalid longitude
            )
    
    def test_invalid_latitude(self):
        """Test that invalid latitude is rejected."""
        with pytest.raises(ValueError, match="Latitude must be between"):
            Coordinates(
                type="Point",
                coordinates=[75.8577, 100.0]  # Invalid latitude
            )
    
    def test_wrong_coordinate_count(self):
        """Test that wrong number of coordinates is rejected."""
        with pytest.raises(ValueError, match="Coordinates must be"):
            Coordinates(
                type="Point",
                coordinates=[75.8577]  # Missing latitude
            )


class TestLocation:
    """Test Location model."""
    
    def test_create_location_from_lat_lon(self):
        """Test creating location from latitude and longitude."""
        location = Location.from_lat_lon(
            user_id="driver123",
            user_type="driver",
            latitude=22.7196,
            longitude=75.8577,
            address="Vijay Nagar, Indore",
            status="available"
        )
        
        assert location.user_id == "driver123"
        assert location.user_type == "driver"
        assert location.get_latitude() == 22.7196
        assert location.get_longitude() == 75.8577
        assert location.address == "Vijay Nagar, Indore"
        assert location.status == "available"
        assert location.city == "Indore"
    
    def test_location_with_coordinates(self):
        """Test creating location with Coordinates object."""
        location = Location(
            user_id="driver456",
            user_type="driver",
            location=Coordinates(
                type="Point",
                coordinates=[75.8577, 22.7196]
            ),
            address="MG Road, Indore"
        )
        
        assert location.user_id == "driver456"
        assert location.get_latitude() == 22.7196
        assert location.get_longitude() == 75.8577
    
    def test_location_timestamp_auto_generated(self):
        """Test that timestamp is automatically generated."""
        before = datetime.utcnow()
        location = Location.from_lat_lon(
            user_id="driver789",
            user_type="driver",
            latitude=22.7196,
            longitude=75.8577
        )
        after = datetime.utcnow()
        
        assert before <= location.timestamp <= after
    
    def test_location_to_dict(self):
        """Test converting location to dictionary."""
        location = Location.from_lat_lon(
            user_id="driver123",
            user_type="driver",
            latitude=22.7196,
            longitude=75.8577,
            address="Test Address",
            status="available"
        )
        
        data = location.to_dict()
        
        assert data["user_id"] == "driver123"
        assert data["user_type"] == "driver"
        assert data["location"]["type"] == "Point"
        assert data["location"]["coordinates"] == [75.8577, 22.7196]
        assert data["address"] == "Test Address"
        assert data["status"] == "available"
        assert "_id" not in data  # Should be removed if None
    
    def test_location_default_city(self):
        """Test that city defaults to Indore."""
        location = Location.from_lat_lon(
            user_id="driver123",
            user_type="driver",
            latitude=22.7196,
            longitude=75.8577
        )
        
        assert location.city == "Indore"


class TestLocationHistory:
    """Test LocationHistory model."""
    
    def test_create_location_history(self):
        """Test creating location history."""
        history = LocationHistory(
            ride_id="ride123",
            driver_id="driver456"
        )
        
        assert history.ride_id == "ride123"
        assert history.driver_id == "driver456"
        assert history.locations == []
        assert history.ended_at is None
    
    def test_add_location_to_history(self):
        """Test adding locations to history."""
        history = LocationHistory(
            ride_id="ride123",
            driver_id="driver456"
        )
        
        location1 = Location.from_lat_lon(
            user_id="driver456",
            user_type="driver",
            latitude=22.7196,
            longitude=75.8577
        )
        
        location2 = Location.from_lat_lon(
            user_id="driver456",
            user_type="driver",
            latitude=22.7200,
            longitude=75.8580
        )
        
        history.add_location(location1)
        history.add_location(location2)
        
        assert len(history.locations) == 2
        assert history.locations[0].get_latitude() == 22.7196
        assert history.locations[1].get_latitude() == 22.7200
    
    def test_location_history_to_dict(self):
        """Test converting location history to dictionary."""
        history = LocationHistory(
            ride_id="ride123",
            driver_id="driver456",
            total_distance=5.5
        )
        
        data = history.to_dict()
        
        assert data["ride_id"] == "ride123"
        assert data["driver_id"] == "driver456"
        assert data["total_distance"] == 5.5
        assert "_id" not in data  # Should be removed if None


class TestLocationIndexes:
    """Test that location indexes are properly defined."""
    
    def test_location_indexes_defined(self):
        """Test that location indexes are defined."""
        from app.models.location import LOCATION_INDEXES
        
        assert len(LOCATION_INDEXES) == 4
        
        # Check for geospatial index
        geo_index = next(idx for idx in LOCATION_INDEXES if idx["name"] == "location_2dsphere_idx")
        assert geo_index["keys"] == [("location", "2dsphere")]
        
        # Check for user_timestamp index
        user_time_index = next(idx for idx in LOCATION_INDEXES if idx["name"] == "user_timestamp_idx")
        assert user_time_index["keys"] == [("user_id", 1), ("timestamp", -1)]
    
    def test_location_history_indexes_defined(self):
        """Test that location history indexes are defined."""
        from app.models.location import LOCATION_HISTORY_INDEXES
        
        assert len(LOCATION_HISTORY_INDEXES) == 2
        
        # Check for ride_id unique index
        ride_index = next(idx for idx in LOCATION_HISTORY_INDEXES if idx["name"] == "ride_id_idx")
        assert ride_index["keys"] == [("ride_id", 1)]
        assert ride_index["unique"] is True



class TestBoundaryValidation:
    """Test boundary validation for Indore service area.
    Tests Requirements 2.4, 13.6
    """
    
    def test_location_within_boundaries(self):
        """Test that locations within Indore boundaries are accepted."""
        from app.services.location_service import LocationService
        from unittest.mock import MagicMock
        
        service = LocationService(MagicMock())
        
        # Test center of Indore
        assert service.is_within_service_area(22.7196, 75.8577) is True
        
        # Test near boundaries but still inside
        assert service.is_within_service_area(22.65, 75.75) is True
        assert service.is_within_service_area(22.75, 75.85) is True
    
    def test_location_outside_boundaries(self):
        """Test that locations outside Indore boundaries are rejected."""
        from app.services.location_service import LocationService
        from unittest.mock import MagicMock
        
        service = LocationService(MagicMock())
        
        # Test latitude too low
        assert service.is_within_service_area(22.5, 75.8) is False
        
        # Test latitude too high
        assert service.is_within_service_area(22.9, 75.8) is False
        
        # Test longitude too low
        assert service.is_within_service_area(22.7, 75.6) is False
        
        # Test longitude too high
        assert service.is_within_service_area(22.7, 76.0) is False
        
        # Test completely outside
        assert service.is_within_service_area(28.6139, 77.2090) is False  # Delhi
    
    def test_location_at_exact_boundaries(self):
        """Test locations at exact boundary coordinates."""
        from app.services.location_service import LocationService
        from unittest.mock import MagicMock
        
        service = LocationService(MagicMock())
        
        # Test exact min boundaries (should be included)
        assert service.is_within_service_area(22.6, 75.7) is True
        
        # Test exact max boundaries (should be included)
        assert service.is_within_service_area(22.8, 75.9) is True
        
        # Test just outside min boundaries
        assert service.is_within_service_area(22.599, 75.699) is False
        
        # Test just outside max boundaries
        assert service.is_within_service_area(22.801, 75.901) is False
    
    def test_validate_location_boundaries_valid(self):
        """Test validate_location_boundaries with valid location."""
        from app.services.location_service import LocationService
        from unittest.mock import MagicMock
        
        service = LocationService(MagicMock())
        
        result = service.validate_location_boundaries(22.7196, 75.8577)
        
        assert result["valid"] is True
        assert result["message"] == "Location is within service area"
        assert result["latitude"] == 22.7196
        assert result["longitude"] == 75.8577
    
    def test_validate_location_boundaries_invalid(self):
        """Test validate_location_boundaries with invalid location."""
        from app.services.location_service import LocationService
        from unittest.mock import MagicMock
        
        service = LocationService(MagicMock())
        
        result = service.validate_location_boundaries(28.6139, 77.2090)  # Delhi
        
        assert result["valid"] is False
        assert "outside Indore service area" in result["message"]
        assert result["latitude"] == 28.6139
        assert result["longitude"] == 77.2090
    
    def test_boundary_constants(self):
        """Test that boundary constants are correctly defined."""
        from app.services.location_service import LocationService
        
        assert LocationService.INDORE_BOUNDARY["min_latitude"] == 22.6
        assert LocationService.INDORE_BOUNDARY["max_latitude"] == 22.8
        assert LocationService.INDORE_BOUNDARY["min_longitude"] == 75.7
        assert LocationService.INDORE_BOUNDARY["max_longitude"] == 75.9
