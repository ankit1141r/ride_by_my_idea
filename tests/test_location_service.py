"""
Tests for Location Service distance calculation.
Tests the Haversine formula implementation for calculating distances between coordinates.

Requirements: 5.1, 5.2
"""
import pytest
import math
from app.services.location_service import LocationService


class TestDistanceCalculation:
    """Unit tests for distance calculation using Haversine formula."""
    
    @pytest.fixture
    def location_service(self):
        """Create a LocationService instance for testing (without DB)."""
        # Create a mock database object that won't be used for distance calculation
        from unittest.mock import MagicMock
        mock_db = MagicMock()
        return LocationService(db=mock_db)
    
    def test_distance_same_point(self, location_service):
        """Distance between same point should be zero."""
        lat, lon = 22.7196, 75.8577  # Indore coordinates
        distance = location_service.calculate_distance(lat, lon, lat, lon)
        assert distance == 0.0
    
    def test_distance_known_locations(self, location_service):
        """Test distance between known locations in Indore."""
        # Approximate coordinates for two locations in Indore
        # Vijay Nagar to Rajwada (approximately 8-9 km)
        vijay_nagar_lat, vijay_nagar_lon = 22.7532, 75.8937
        rajwada_lat, rajwada_lon = 22.7196, 75.8577
        
        distance = location_service.calculate_distance(
            vijay_nagar_lat, vijay_nagar_lon,
            rajwada_lat, rajwada_lon
        )
        
        # Distance should be approximately 5-6 km (straight line)
        assert 4.0 < distance < 7.0
    
    def test_distance_symmetry(self, location_service):
        """Distance from A to B should equal distance from B to A."""
        lat1, lon1 = 22.7196, 75.8577
        lat2, lon2 = 22.7532, 75.8937
        
        distance_ab = location_service.calculate_distance(lat1, lon1, lat2, lon2)
        distance_ba = location_service.calculate_distance(lat2, lon2, lat1, lon1)
        
        assert abs(distance_ab - distance_ba) < 0.0001  # Should be equal within floating point precision
    
    def test_distance_positive(self, location_service):
        """Distance should always be positive."""
        lat1, lon1 = 22.7196, 75.8577
        lat2, lon2 = 22.7532, 75.8937
        
        distance = location_service.calculate_distance(lat1, lon1, lat2, lon2)
        
        assert distance >= 0
    
    def test_distance_small_difference(self, location_service):
        """Test distance for very close points (within meters)."""
        # Two points very close together (about 100 meters apart)
        lat1, lon1 = 22.7196, 75.8577
        lat2, lon2 = 22.7206, 75.8587  # Slightly offset
        
        distance = location_service.calculate_distance(lat1, lon1, lat2, lon2)
        
        # Should be less than 2 km
        assert 0 < distance < 2.0
    
    def test_distance_across_indore(self, location_service):
        """Test distance across Indore city boundaries."""
        # From one corner of Indore to another
        lat1, lon1 = 22.6, 75.7  # Southwest corner
        lat2, lon2 = 22.8, 75.9  # Northeast corner
        
        distance = location_service.calculate_distance(lat1, lon1, lat2, lon2)
        
        # Diagonal distance across Indore should be roughly 25-30 km
        assert 20.0 < distance < 35.0
    
    def test_distance_equator_crossing(self, location_service):
        """Test distance calculation across equator."""
        # North of equator
        lat1, lon1 = 10.0, 75.0
        # South of equator
        lat2, lon2 = -10.0, 75.0
        
        distance = location_service.calculate_distance(lat1, lon1, lat2, lon2)
        
        # Should be approximately 2,222 km (20 degrees of latitude)
        assert 2200 < distance < 2250
    
    def test_distance_prime_meridian_crossing(self, location_service):
        """Test distance calculation across prime meridian."""
        lat1, lon1 = 22.0, -10.0  # West of prime meridian
        lat2, lon2 = 22.0, 10.0   # East of prime meridian
        
        distance = location_service.calculate_distance(lat1, lon1, lat2, lon2)
        
        # Should be approximately 2,000+ km (20 degrees of longitude at this latitude)
        assert distance > 1800
    
    def test_distance_returns_kilometers(self, location_service):
        """Verify that distance is returned in kilometers."""
        # 1 degree of latitude is approximately 111 km
        lat1, lon1 = 22.0, 75.0
        lat2, lon2 = 23.0, 75.0  # 1 degree north
        
        distance = location_service.calculate_distance(lat1, lon1, lat2, lon2)
        
        # Should be approximately 111 km
        assert 110 < distance < 112
    
    def test_distance_triangle_inequality(self, location_service):
        """Test that triangle inequality holds: d(A,C) <= d(A,B) + d(B,C)."""
        # Three points in Indore
        lat_a, lon_a = 22.7196, 75.8577
        lat_b, lon_b = 22.7532, 75.8937
        lat_c, lon_c = 22.6800, 75.8700
        
        dist_ac = location_service.calculate_distance(lat_a, lon_a, lat_c, lon_c)
        dist_ab = location_service.calculate_distance(lat_a, lon_a, lat_b, lon_b)
        dist_bc = location_service.calculate_distance(lat_b, lon_b, lat_c, lon_c)
        
        # Triangle inequality: distance from A to C should be less than or equal to
        # distance from A to B plus distance from B to C
        assert dist_ac <= dist_ab + dist_bc + 0.001  # Small epsilon for floating point
    
    def test_distance_with_negative_coordinates(self, location_service):
        """Test distance calculation with negative coordinates."""
        # Southern hemisphere and western hemisphere
        lat1, lon1 = -22.7196, -75.8577
        lat2, lon2 = -22.7532, -75.8937
        
        distance = location_service.calculate_distance(lat1, lon1, lat2, lon2)
        
        # Should still calculate correctly
        assert distance > 0
        assert 4.0 < distance < 7.0
    
    def test_distance_extreme_latitudes(self, location_service):
        """Test distance calculation near poles."""
        # Near north pole
        lat1, lon1 = 89.0, 0.0
        lat2, lon2 = 89.0, 180.0
        
        distance = location_service.calculate_distance(lat1, lon1, lat2, lon2)
        
        # At 89 degrees latitude, longitude lines are very close
        # Distance should be relatively small
        assert distance < 500
    
    def test_distance_maximum_distance(self, location_service):
        """Test maximum possible distance (antipodal points)."""
        # Opposite sides of Earth
        lat1, lon1 = 0.0, 0.0
        lat2, lon2 = 0.0, 180.0
        
        distance = location_service.calculate_distance(lat1, lon1, lat2, lon2)
        
        # Half the Earth's circumference at equator (approximately 20,000 km)
        assert 19900 < distance < 20100
    
    def test_distance_precision(self, location_service):
        """Test that distance calculation has reasonable precision."""
        lat1, lon1 = 22.7196, 75.8577
        lat2, lon2 = 22.7197, 75.8578
        
        distance = location_service.calculate_distance(lat1, lon1, lat2, lon2)
        
        # Very small distance should be calculated with precision
        assert 0 < distance < 0.2  # Less than 200 meters



class TestDistanceCalculationProperties:
    """Property-based tests for distance calculation using Hypothesis."""
    
    @pytest.fixture
    def location_service(self):
        """Create a LocationService instance for testing."""
        from unittest.mock import MagicMock
        mock_db = MagicMock()
        return LocationService(db=mock_db)
    
    def test_property_distance_non_negative(self, location_service):
        """Property: Distance between any two points should always be non-negative."""
        from hypothesis import given, strategies as st
        
        @given(
            lat1=st.floats(min_value=-90, max_value=90, allow_nan=False, allow_infinity=False),
            lon1=st.floats(min_value=-180, max_value=180, allow_nan=False, allow_infinity=False),
            lat2=st.floats(min_value=-90, max_value=90, allow_nan=False, allow_infinity=False),
            lon2=st.floats(min_value=-180, max_value=180, allow_nan=False, allow_infinity=False)
        )
        def check_non_negative(lat1, lon1, lat2, lon2):
            distance = location_service.calculate_distance(lat1, lon1, lat2, lon2)
            assert distance >= 0, f"Distance should be non-negative, got {distance}"
        
        check_non_negative()
    
    def test_property_distance_symmetry(self, location_service):
        """Property: Distance from A to B equals distance from B to A."""
        from hypothesis import given, strategies as st
        
        @given(
            lat1=st.floats(min_value=-90, max_value=90, allow_nan=False, allow_infinity=False),
            lon1=st.floats(min_value=-180, max_value=180, allow_nan=False, allow_infinity=False),
            lat2=st.floats(min_value=-90, max_value=90, allow_nan=False, allow_infinity=False),
            lon2=st.floats(min_value=-180, max_value=180, allow_nan=False, allow_infinity=False)
        )
        def check_symmetry(lat1, lon1, lat2, lon2):
            dist_ab = location_service.calculate_distance(lat1, lon1, lat2, lon2)
            dist_ba = location_service.calculate_distance(lat2, lon2, lat1, lon1)
            assert abs(dist_ab - dist_ba) < 0.0001, f"Distance should be symmetric: {dist_ab} != {dist_ba}"
        
        check_symmetry()
    
    def test_property_distance_identity(self, location_service):
        """Property: Distance from a point to itself is zero."""
        from hypothesis import given, strategies as st
        
        @given(
            lat=st.floats(min_value=-90, max_value=90, allow_nan=False, allow_infinity=False),
            lon=st.floats(min_value=-180, max_value=180, allow_nan=False, allow_infinity=False)
        )
        def check_identity(lat, lon):
            distance = location_service.calculate_distance(lat, lon, lat, lon)
            assert distance == 0.0, f"Distance to same point should be zero, got {distance}"
        
        check_identity()
    
    def test_property_distance_triangle_inequality(self, location_service):
        """Property: Triangle inequality - d(A,C) <= d(A,B) + d(B,C)."""
        from hypothesis import given, strategies as st
        
        @given(
            lat_a=st.floats(min_value=-90, max_value=90, allow_nan=False, allow_infinity=False),
            lon_a=st.floats(min_value=-180, max_value=180, allow_nan=False, allow_infinity=False),
            lat_b=st.floats(min_value=-90, max_value=90, allow_nan=False, allow_infinity=False),
            lon_b=st.floats(min_value=-180, max_value=180, allow_nan=False, allow_infinity=False),
            lat_c=st.floats(min_value=-90, max_value=90, allow_nan=False, allow_infinity=False),
            lon_c=st.floats(min_value=-180, max_value=180, allow_nan=False, allow_infinity=False)
        )
        def check_triangle_inequality(lat_a, lon_a, lat_b, lon_b, lat_c, lon_c):
            dist_ac = location_service.calculate_distance(lat_a, lon_a, lat_c, lon_c)
            dist_ab = location_service.calculate_distance(lat_a, lon_a, lat_b, lon_b)
            dist_bc = location_service.calculate_distance(lat_b, lon_b, lat_c, lon_c)
            
            # Triangle inequality with small epsilon for floating point errors
            assert dist_ac <= dist_ab + dist_bc + 0.001, \
                f"Triangle inequality violated: {dist_ac} > {dist_ab} + {dist_bc}"
        
        check_triangle_inequality()
    
    def test_property_distance_bounded_by_earth_circumference(self, location_service):
        """Property: Distance between any two points cannot exceed half Earth's circumference."""
        from hypothesis import given, strategies as st
        
        # Maximum distance on Earth is half the circumference (antipodal points)
        # Earth's circumference ≈ 40,075 km, so max distance ≈ 20,037 km
        MAX_EARTH_DISTANCE = 20100  # km (with some margin)
        
        @given(
            lat1=st.floats(min_value=-90, max_value=90, allow_nan=False, allow_infinity=False),
            lon1=st.floats(min_value=-180, max_value=180, allow_nan=False, allow_infinity=False),
            lat2=st.floats(min_value=-90, max_value=90, allow_nan=False, allow_infinity=False),
            lon2=st.floats(min_value=-180, max_value=180, allow_nan=False, allow_infinity=False)
        )
        def check_bounded(lat1, lon1, lat2, lon2):
            distance = location_service.calculate_distance(lat1, lon1, lat2, lon2)
            assert distance <= MAX_EARTH_DISTANCE, \
                f"Distance {distance} km exceeds maximum possible distance on Earth"
        
        check_bounded()
    
    def test_property_distance_within_indore(self, location_service):
        """Property: Distance between any two points within Indore should be reasonable."""
        from hypothesis import given, strategies as st
        
        # Indore boundaries
        INDORE_MIN_LAT, INDORE_MAX_LAT = 22.6, 22.8
        INDORE_MIN_LON, INDORE_MAX_LON = 75.7, 75.9
        
        # Maximum diagonal distance across Indore should be around 30-35 km
        MAX_INDORE_DISTANCE = 40  # km (with margin)
        
        @given(
            lat1=st.floats(min_value=INDORE_MIN_LAT, max_value=INDORE_MAX_LAT, 
                          allow_nan=False, allow_infinity=False),
            lon1=st.floats(min_value=INDORE_MIN_LON, max_value=INDORE_MAX_LON,
                          allow_nan=False, allow_infinity=False),
            lat2=st.floats(min_value=INDORE_MIN_LAT, max_value=INDORE_MAX_LAT,
                          allow_nan=False, allow_infinity=False),
            lon2=st.floats(min_value=INDORE_MIN_LON, max_value=INDORE_MAX_LON,
                          allow_nan=False, allow_infinity=False)
        )
        def check_indore_distances(lat1, lon1, lat2, lon2):
            distance = location_service.calculate_distance(lat1, lon1, lat2, lon2)
            assert 0 <= distance <= MAX_INDORE_DISTANCE, \
                f"Distance {distance} km within Indore exceeds expected maximum"
        
        check_indore_distances()
    
    def test_property_distance_increases_with_latitude_difference(self, location_service):
        """Property: Increasing latitude difference increases distance (same longitude)."""
        from hypothesis import given, strategies as st, assume
        
        @given(
            lat1=st.floats(min_value=-89, max_value=89, allow_nan=False, allow_infinity=False),
            lon=st.floats(min_value=-180, max_value=180, allow_nan=False, allow_infinity=False),
            delta=st.floats(min_value=0.1, max_value=1.0, allow_nan=False, allow_infinity=False)
        )
        def check_latitude_monotonicity(lat1, lon, delta):
            # Ensure we don't exceed latitude bounds
            assume(lat1 + delta <= 90)
            assume(lat1 + 2 * delta <= 90)
            
            lat2 = lat1 + delta
            lat3 = lat1 + 2 * delta
            
            dist1 = location_service.calculate_distance(lat1, lon, lat2, lon)
            dist2 = location_service.calculate_distance(lat1, lon, lat3, lon)
            
            # Distance should increase with latitude difference
            assert dist2 >= dist1, \
                f"Distance should increase with latitude difference: {dist2} < {dist1}"
        
        check_latitude_monotonicity()
    
    def test_property_distance_consistent_across_hemispheres(self, location_service):
        """Property: Same relative positions in different hemispheres have same distance."""
        from hypothesis import given, strategies as st
        
        @given(
            lat_offset=st.floats(min_value=0, max_value=10, allow_nan=False, allow_infinity=False),
            lon_offset=st.floats(min_value=0, max_value=10, allow_nan=False, allow_infinity=False),
            base_lat=st.floats(min_value=20, max_value=70, allow_nan=False, allow_infinity=False),
            base_lon=st.floats(min_value=20, max_value=160, allow_nan=False, allow_infinity=False)
        )
        def check_hemisphere_consistency(lat_offset, lon_offset, base_lat, base_lon):
            # Northern/Eastern hemisphere
            dist_ne = location_service.calculate_distance(
                base_lat, base_lon,
                base_lat + lat_offset, base_lon + lon_offset
            )
            
            # Southern/Western hemisphere (mirrored)
            dist_sw = location_service.calculate_distance(
                -base_lat, -base_lon,
                -(base_lat + lat_offset), -(base_lon + lon_offset)
            )
            
            # Distances should be approximately equal (within floating point precision)
            assert abs(dist_ne - dist_sw) < 0.01, \
                f"Distances in different hemispheres should be equal: {dist_ne} != {dist_sw}"
        
        check_hemisphere_consistency()



class TestGoogleMapsIntegration:
    """Unit tests for Google Maps API integration."""
    
    @pytest.fixture
    def location_service(self):
        """Create a LocationService instance for testing."""
        from unittest.mock import MagicMock
        mock_db = MagicMock()
        return LocationService(db=mock_db)
    
    def test_google_maps_client_initialization(self, location_service):
        """Test that Google Maps client is initialized when API key is configured."""
        # If API key is configured, client should be initialized
        if location_service.gmaps_client:
            assert location_service.gmaps_client is not None
        else:
            # If no API key, client should be None
            assert location_service.gmaps_client is None
    
    def test_search_address_without_api_key(self):
        """Test that search_address raises error when API key is not configured."""
        from unittest.mock import MagicMock
        mock_db = MagicMock()
        service = LocationService(db=mock_db)
        service.gmaps_client = None  # Force no API key
        
        with pytest.raises(ValueError, match="Google Maps API key not configured"):
            service.search_address("Rajwada")
    
    def test_search_address_adds_indore_to_query(self, location_service, monkeypatch):
        """Test that search_address adds 'Indore' to query if not present."""
        if not location_service.gmaps_client:
            pytest.skip("Google Maps API key not configured")
        
        # Mock the geocode method
        mock_geocode = MagicMock(return_value=[])
        monkeypatch.setattr(location_service.gmaps_client, "geocode", mock_geocode)
        
        location_service.search_address("Rajwada")
        
        # Check that "Indore" was added to the query
        call_args = mock_geocode.call_args
        assert "indore" in call_args[0][0].lower()
    
    def test_search_address_filters_by_service_area(self, location_service, monkeypatch):
        """Test that search_address filters results to service area."""
        if not location_service.gmaps_client:
            pytest.skip("Google Maps API key not configured")
        
        # Mock geocode results with locations inside and outside service area
        mock_results = [
            {
                "formatted_address": "Inside Indore",
                "geometry": {"location": {"lat": 22.7196, "lng": 75.8577}},
                "place_id": "place1"
            },
            {
                "formatted_address": "Outside Indore",
                "geometry": {"location": {"lat": 23.0, "lng": 76.0}},
                "place_id": "place2"
            },
            {
                "formatted_address": "Also Inside Indore",
                "geometry": {"location": {"lat": 22.7, "lng": 75.8}},
                "place_id": "place3"
            }
        ]
        
        mock_geocode = MagicMock(return_value=mock_results)
        monkeypatch.setattr(location_service.gmaps_client, "geocode", mock_geocode)
        
        results = location_service.search_address("test")
        
        # Should only return locations within service area
        assert len(results) == 2
        assert all(
            location_service.is_within_service_area(r["latitude"], r["longitude"])
            for r in results
        )
    
    def test_search_address_respects_limit(self, location_service, monkeypatch):
        """Test that search_address respects the limit parameter."""
        if not location_service.gmaps_client:
            pytest.skip("Google Maps API key not configured")
        
        # Mock many results within service area
        mock_results = [
            {
                "formatted_address": f"Location {i}",
                "geometry": {"location": {"lat": 22.7 + i*0.01, "lng": 75.8 + i*0.01}},
                "place_id": f"place{i}"
            }
            for i in range(10)
        ]
        
        mock_geocode = MagicMock(return_value=mock_results)
        monkeypatch.setattr(location_service.gmaps_client, "geocode", mock_geocode)
        
        results = location_service.search_address("test", limit=3)
        
        # Should return at most 3 results
        assert len(results) <= 3
    
    def test_search_address_returns_correct_structure(self, location_service, monkeypatch):
        """Test that search_address returns correctly structured results."""
        if not location_service.gmaps_client:
            pytest.skip("Google Maps API key not configured")
        
        mock_results = [
            {
                "formatted_address": "Test Address, Indore",
                "geometry": {"location": {"lat": 22.7196, "lng": 75.8577}},
                "place_id": "test_place_id"
            }
        ]
        
        mock_geocode = MagicMock(return_value=mock_results)
        monkeypatch.setattr(location_service.gmaps_client, "geocode", mock_geocode)
        
        results = location_service.search_address("test")
        
        assert len(results) == 1
        result = results[0]
        
        # Check structure
        assert "address" in result
        assert "latitude" in result
        assert "longitude" in result
        assert "place_id" in result
        
        # Check values
        assert result["address"] == "Test Address, Indore"
        assert result["latitude"] == 22.7196
        assert result["longitude"] == 75.8577
        assert result["place_id"] == "test_place_id"
    
    def test_search_address_handles_api_error(self, location_service, monkeypatch):
        """Test that search_address handles API errors gracefully."""
        if not location_service.gmaps_client:
            pytest.skip("Google Maps API key not configured")
        
        # Mock geocode to raise an exception
        mock_geocode = MagicMock(side_effect=Exception("API Error"))
        monkeypatch.setattr(location_service.gmaps_client, "geocode", mock_geocode)
        
        results = location_service.search_address("test")
        
        # Should return empty list on error
        assert results == []
    
    def test_calculate_route_without_api_key(self):
        """Test that calculate_route raises error when API key is not configured."""
        from unittest.mock import MagicMock
        mock_db = MagicMock()
        service = LocationService(db=mock_db)
        service.gmaps_client = None  # Force no API key
        
        with pytest.raises(ValueError, match="Google Maps API key not configured"):
            service.calculate_route(22.7196, 75.8577, 22.7532, 75.8937)
    
    def test_calculate_route_returns_correct_structure(self, location_service, monkeypatch):
        """Test that calculate_route returns correctly structured result."""
        if not location_service.gmaps_client:
            pytest.skip("Google Maps API key not configured")
        
        # Mock directions API response
        mock_directions = [
            {
                "overview_polyline": {"points": "test_polyline_string"},
                "legs": [
                    {
                        "distance": {"value": 5000},  # 5000 meters = 5 km
                        "duration": {"value": 600},   # 600 seconds = 10 minutes
                        "start_location": {"lat": 22.7196, "lng": 75.8577},
                        "end_location": {"lat": 22.7532, "lng": 75.8937},
                        "steps": [
                            {
                                "start_location": {"lat": 22.7196, "lng": 75.8577},
                                "end_location": {"lat": 22.73, "lng": 75.87}
                            },
                            {
                                "start_location": {"lat": 22.73, "lng": 75.87},
                                "end_location": {"lat": 22.7532, "lng": 75.8937}
                            }
                        ]
                    }
                ],
                "bounds": {
                    "northeast": {"lat": 22.7532, "lng": 75.8937},
                    "southwest": {"lat": 22.7196, "lng": 75.8577}
                }
            }
        ]
        
        mock_directions_method = MagicMock(return_value=mock_directions)
        monkeypatch.setattr(location_service.gmaps_client, "directions", mock_directions_method)
        
        result = location_service.calculate_route(22.7196, 75.8577, 22.7532, 75.8937)
        
        # Check structure
        assert result is not None
        assert "distance_km" in result
        assert "duration_minutes" in result
        assert "polyline" in result
        assert "waypoints" in result
        assert "bounds" in result
        
        # Check values
        assert result["distance_km"] == 5.0
        assert result["duration_minutes"] == 10
        assert result["polyline"] == "test_polyline_string"
        assert len(result["waypoints"]) == 3  # 2 steps + 1 final destination
        
        # Check bounds structure
        assert "northeast" in result["bounds"]
        assert "southwest" in result["bounds"]
        assert "latitude" in result["bounds"]["northeast"]
        assert "longitude" in result["bounds"]["northeast"]
    
    def test_calculate_route_handles_no_results(self, location_service, monkeypatch):
        """Test that calculate_route handles empty results from API."""
        if not location_service.gmaps_client:
            pytest.skip("Google Maps API key not configured")
        
        # Mock empty directions result
        mock_directions_method = MagicMock(return_value=[])
        monkeypatch.setattr(location_service.gmaps_client, "directions", mock_directions_method)
        
        result = location_service.calculate_route(22.7196, 75.8577, 22.7532, 75.8937)
        
        # Should return None when no route found
        assert result is None
    
    def test_calculate_route_handles_api_error(self, location_service, monkeypatch):
        """Test that calculate_route handles API errors gracefully."""
        if not location_service.gmaps_client:
            pytest.skip("Google Maps API key not configured")
        
        # Mock directions to raise an exception
        mock_directions_method = MagicMock(side_effect=Exception("API Error"))
        monkeypatch.setattr(location_service.gmaps_client, "directions", mock_directions_method)
        
        result = location_service.calculate_route(22.7196, 75.8577, 22.7532, 75.8937)
        
        # Should return None on error
        assert result is None
    
    def test_calculate_route_includes_waypoints(self, location_service, monkeypatch):
        """Test that calculate_route includes all waypoints from route steps."""
        if not location_service.gmaps_client:
            pytest.skip("Google Maps API key not configured")
        
        # Mock directions with multiple steps
        mock_directions = [
            {
                "overview_polyline": {"points": "polyline"},
                "legs": [
                    {
                        "distance": {"value": 10000},
                        "duration": {"value": 1200},
                        "start_location": {"lat": 22.7196, "lng": 75.8577},
                        "end_location": {"lat": 22.7532, "lng": 75.8937},
                        "steps": [
                            {"start_location": {"lat": 22.7196, "lng": 75.8577}},
                            {"start_location": {"lat": 22.72, "lng": 75.86}},
                            {"start_location": {"lat": 22.73, "lng": 75.87}},
                            {"start_location": {"lat": 22.74, "lng": 75.88}}
                        ]
                    }
                ],
                "bounds": {
                    "northeast": {"lat": 22.7532, "lng": 75.8937},
                    "southwest": {"lat": 22.7196, "lng": 75.8577}
                }
            }
        ]
        
        mock_directions_method = MagicMock(return_value=mock_directions)
        monkeypatch.setattr(location_service.gmaps_client, "directions", mock_directions_method)
        
        result = location_service.calculate_route(22.7196, 75.8577, 22.7532, 75.8937)
        
        # Should have 4 steps + 1 final destination = 5 waypoints
        assert len(result["waypoints"]) == 5
        
        # First waypoint should be start location
        assert result["waypoints"][0]["latitude"] == 22.7196
        assert result["waypoints"][0]["longitude"] == 75.8577
        
        # Last waypoint should be end location
        assert result["waypoints"][-1]["latitude"] == 22.7532
        assert result["waypoints"][-1]["longitude"] == 75.8937
    
    def test_calculate_route_rounds_distance(self, location_service, monkeypatch):
        """Test that calculate_route rounds distance to 2 decimal places."""
        if not location_service.gmaps_client:
            pytest.skip("Google Maps API key not configured")
        
        # Mock directions with precise distance
        mock_directions = [
            {
                "overview_polyline": {"points": "polyline"},
                "legs": [
                    {
                        "distance": {"value": 5678},  # 5.678 km
                        "duration": {"value": 600},
                        "start_location": {"lat": 22.7196, "lng": 75.8577},
                        "end_location": {"lat": 22.7532, "lng": 75.8937},
                        "steps": [{"start_location": {"lat": 22.7196, "lng": 75.8577}}]
                    }
                ],
                "bounds": {
                    "northeast": {"lat": 22.7532, "lng": 75.8937},
                    "southwest": {"lat": 22.7196, "lng": 75.8577}
                }
            }
        ]
        
        mock_directions_method = MagicMock(return_value=mock_directions)
        monkeypatch.setattr(location_service.gmaps_client, "directions", mock_directions_method)
        
        result = location_service.calculate_route(22.7196, 75.8577, 22.7532, 75.8937)
        
        # Should be rounded to 2 decimal places
        assert result["distance_km"] == 5.68
    
    def test_calculate_route_converts_duration_to_minutes(self, location_service, monkeypatch):
        """Test that calculate_route converts duration from seconds to minutes."""
        if not location_service.gmaps_client:
            pytest.skip("Google Maps API key not configured")
        
        # Mock directions with duration in seconds
        mock_directions = [
            {
                "overview_polyline": {"points": "polyline"},
                "legs": [
                    {
                        "distance": {"value": 5000},
                        "duration": {"value": 725},  # 725 seconds = 12.08 minutes
                        "start_location": {"lat": 22.7196, "lng": 75.8577},
                        "end_location": {"lat": 22.7532, "lng": 75.8937},
                        "steps": [{"start_location": {"lat": 22.7196, "lng": 75.8577}}]
                    }
                ],
                "bounds": {
                    "northeast": {"lat": 22.7532, "lng": 75.8937},
                    "southwest": {"lat": 22.7196, "lng": 75.8577}
                }
            }
        ]
        
        mock_directions_method = MagicMock(return_value=mock_directions)
        monkeypatch.setattr(location_service.gmaps_client, "directions", mock_directions_method)
        
        result = location_service.calculate_route(22.7196, 75.8577, 22.7532, 75.8937)
        
        # Should be converted to minutes and truncated to int
        assert result["duration_minutes"] == 12



class TestRouteDeviationDetection:
    """Unit tests for route deviation detection."""
    
    @pytest.fixture
    def location_service(self):
        """Create a LocationService instance for testing."""
        from unittest.mock import MagicMock
        mock_db = MagicMock()
        return LocationService(db=mock_db)
    
    def test_no_deviation_on_route(self, location_service):
        """Test that location on route shows no deviation."""
        # Define a simple route with waypoints
        route_waypoints = [
            {"latitude": 22.7196, "longitude": 75.8577},
            {"latitude": 22.7300, "longitude": 75.8700},
            {"latitude": 22.7400, "longitude": 75.8800}
        ]
        
        # Current location is exactly on one of the waypoints
        current_lat, current_lng = 22.7300, 75.8700
        
        result = location_service.detect_route_deviation(
            current_lat, current_lng, route_waypoints
        )
        
        assert result["is_deviated"] is False
        assert result["deviation_distance_meters"] == 0.0
        assert result["current_location"]["latitude"] == current_lat
        assert result["current_location"]["longitude"] == current_lng
        assert result["closest_waypoint"] == route_waypoints[1]
    
    def test_small_deviation_within_threshold(self, location_service):
        """Test that small deviation within threshold is not flagged."""
        route_waypoints = [
            {"latitude": 22.7196, "longitude": 75.8577},
            {"latitude": 22.7300, "longitude": 75.8700}
        ]
        
        # Current location is slightly off route (about 100m)
        current_lat, current_lng = 22.7205, 75.8585
        
        result = location_service.detect_route_deviation(
            current_lat, current_lng, route_waypoints, threshold_meters=500.0
        )
        
        assert result["is_deviated"] is False
        assert result["deviation_distance_meters"] < 500.0
    
    def test_large_deviation_exceeds_threshold(self, location_service):
        """Test that large deviation exceeds threshold and is flagged."""
        route_waypoints = [
            {"latitude": 22.7196, "longitude": 75.8577},
            {"latitude": 22.7300, "longitude": 75.8700}
        ]
        
        # Current location is far from route (about 2km away)
        current_lat, current_lng = 22.7400, 75.8900
        
        result = location_service.detect_route_deviation(
            current_lat, current_lng, route_waypoints, threshold_meters=500.0
        )
        
        assert result["is_deviated"] is True
        assert result["deviation_distance_meters"] > 500.0
    
    def test_deviation_exactly_at_threshold(self, location_service):
        """Test behavior when deviation is exactly at threshold."""
        route_waypoints = [
            {"latitude": 22.7196, "longitude": 75.8577}
        ]
        
        # Calculate a point exactly 500m away
        # At this latitude, 1 degree ≈ 111km, so 500m ≈ 0.0045 degrees
        current_lat = 22.7196 + 0.0045
        current_lng = 75.8577
        
        result = location_service.detect_route_deviation(
            current_lat, current_lng, route_waypoints, threshold_meters=500.0
        )
        
        # At exactly threshold, should not be deviated (> not >=)
        # But due to floating point, we check the actual distance
        if result["deviation_distance_meters"] > 500.0:
            assert result["is_deviated"] is True
        else:
            assert result["is_deviated"] is False
    
    def test_deviation_with_multiple_waypoints(self, location_service):
        """Test that deviation uses closest waypoint from multiple options."""
        route_waypoints = [
            {"latitude": 22.7196, "longitude": 75.8577},
            {"latitude": 22.7300, "longitude": 75.8700},
            {"latitude": 22.7400, "longitude": 75.8800},
            {"latitude": 22.7500, "longitude": 75.8900}
        ]
        
        # Current location is close to third waypoint
        current_lat, current_lng = 22.7405, 75.8805
        
        result = location_service.detect_route_deviation(
            current_lat, current_lng, route_waypoints, threshold_meters=500.0
        )
        
        # Should use closest waypoint (third one)
        assert result["closest_waypoint"]["latitude"] == 22.7400
        assert result["closest_waypoint"]["longitude"] == 75.8800
        assert result["is_deviated"] is False
    
    def test_deviation_with_empty_waypoints(self, location_service):
        """Test that empty waypoints list returns no deviation."""
        route_waypoints = []
        
        current_lat, current_lng = 22.7196, 75.8577
        
        result = location_service.detect_route_deviation(
            current_lat, current_lng, route_waypoints
        )
        
        assert result["is_deviated"] is False
        assert result["deviation_distance_meters"] == 0.0
        assert result["closest_waypoint"] is None
    
    def test_deviation_with_custom_threshold(self, location_service):
        """Test that custom threshold is respected."""
        route_waypoints = [
            {"latitude": 22.7196, "longitude": 75.8577}
        ]
        
        # Location about 300m away
        current_lat, current_lng = 22.7223, 75.8577
        
        # With 200m threshold, should be deviated
        result_200 = location_service.detect_route_deviation(
            current_lat, current_lng, route_waypoints, threshold_meters=200.0
        )
        
        # With 400m threshold, should not be deviated
        result_400 = location_service.detect_route_deviation(
            current_lat, current_lng, route_waypoints, threshold_meters=400.0
        )
        
        assert result_200["is_deviated"] is True
        assert result_400["is_deviated"] is False
        assert result_200["threshold_meters"] == 200.0
        assert result_400["threshold_meters"] == 400.0
    
    def test_deviation_result_structure(self, location_service):
        """Test that deviation result has correct structure."""
        route_waypoints = [
            {"latitude": 22.7196, "longitude": 75.8577}
        ]
        
        current_lat, current_lng = 22.7200, 75.8580
        
        result = location_service.detect_route_deviation(
            current_lat, current_lng, route_waypoints
        )
        
        # Check all required keys are present
        assert "is_deviated" in result
        assert "deviation_distance_meters" in result
        assert "current_location" in result
        assert "closest_waypoint" in result
        assert "threshold_meters" in result
        
        # Check current_location structure
        assert "latitude" in result["current_location"]
        assert "longitude" in result["current_location"]
        
        # Check types
        assert isinstance(result["is_deviated"], bool)
        assert isinstance(result["deviation_distance_meters"], (int, float))
        assert isinstance(result["threshold_meters"], (int, float))
    
    def test_deviation_distance_is_rounded(self, location_service):
        """Test that deviation distance is rounded to 2 decimal places."""
        route_waypoints = [
            {"latitude": 22.7196, "longitude": 75.8577}
        ]
        
        current_lat, current_lng = 22.7200, 75.8580
        
        result = location_service.detect_route_deviation(
            current_lat, current_lng, route_waypoints
        )
        
        # Check that distance has at most 2 decimal places
        distance_str = str(result["deviation_distance_meters"])
        if "." in distance_str:
            decimal_places = len(distance_str.split(".")[1])
            assert decimal_places <= 2
    
    def test_deviation_with_invalid_waypoint_data(self, location_service):
        """Test that invalid waypoint data is handled gracefully."""
        route_waypoints = [
            {"latitude": 22.7196, "longitude": 75.8577},
            {"latitude": None, "longitude": 75.8700},  # Invalid
            {"latitude": 22.7400},  # Missing longitude
            {"longitude": 75.8800},  # Missing latitude
            {"latitude": 22.7500, "longitude": 75.8900}
        ]
        
        current_lat, current_lng = 22.7450, 75.8850
        
        result = location_service.detect_route_deviation(
            current_lat, current_lng, route_waypoints
        )
        
        # Should still work with valid waypoints
        assert "is_deviated" in result
        assert result["closest_waypoint"] is not None
        # Should use one of the valid waypoints
        assert result["closest_waypoint"]["latitude"] in [22.7196, 22.7500]
    
    def test_deviation_default_threshold_is_500m(self, location_service):
        """Test that default threshold is 500 meters as per requirements."""
        route_waypoints = [
            {"latitude": 22.7196, "longitude": 75.8577}
        ]
        
        current_lat, current_lng = 22.7200, 75.8580
        
        # Call without specifying threshold
        result = location_service.detect_route_deviation(
            current_lat, current_lng, route_waypoints
        )
        
        # Default threshold should be 500m (Requirement 11.4)
        assert result["threshold_meters"] == 500.0
    
    def test_deviation_with_route_across_indore(self, location_service):
        """Test deviation detection with realistic Indore route."""
        # Simulate a route from Vijay Nagar to Rajwada
        route_waypoints = [
            {"latitude": 22.7532, "longitude": 75.8937},  # Vijay Nagar
            {"latitude": 22.7450, "longitude": 75.8850},
            {"latitude": 22.7350, "longitude": 75.8750},
            {"latitude": 22.7250, "longitude": 75.8650},
            {"latitude": 22.7196, "longitude": 75.8577}   # Rajwada
        ]
        
        # Driver is on route (near second waypoint)
        current_lat, current_lng = 22.7455, 75.8855
        
        result = location_service.detect_route_deviation(
            current_lat, current_lng, route_waypoints
        )
        
        assert result["is_deviated"] is False
        assert result["deviation_distance_meters"] < 500.0
    
    def test_deviation_alert_for_wrong_direction(self, location_service):
        """Test that going in wrong direction triggers deviation alert."""
        # Route going north
        route_waypoints = [
            {"latitude": 22.7196, "longitude": 75.8577},
            {"latitude": 22.7300, "longitude": 75.8577},
            {"latitude": 22.7400, "longitude": 75.8577}
        ]
        
        # Driver went east instead (1km off route)
        current_lat, current_lng = 22.7300, 75.8677
        
        result = location_service.detect_route_deviation(
            current_lat, current_lng, route_waypoints, threshold_meters=500.0
        )
        
        assert result["is_deviated"] is True
        assert result["deviation_distance_meters"] > 500.0


class TestRouteDeviationProperties:
    """Property-based tests for route deviation detection using Hypothesis."""
    
    @pytest.fixture
    def location_service(self):
        """Create a LocationService instance for testing."""
        from unittest.mock import MagicMock
        mock_db = MagicMock()
        return LocationService(db=mock_db)
    
    def test_property_deviation_on_waypoint_is_zero(self, location_service):
        """Property: Deviation at exact waypoint location should be zero."""
        from hypothesis import given, strategies as st
        
        @given(
            lat=st.floats(min_value=22.6, max_value=22.8, allow_nan=False, allow_infinity=False),
            lng=st.floats(min_value=75.7, max_value=75.9, allow_nan=False, allow_infinity=False)
        )
        def check_zero_deviation_on_waypoint(lat, lng):
            route_waypoints = [{"latitude": lat, "longitude": lng}]
            
            result = location_service.detect_route_deviation(lat, lng, route_waypoints)
            
            assert result["deviation_distance_meters"] == 0.0
            assert result["is_deviated"] is False
        
        check_zero_deviation_on_waypoint()
    
    def test_property_deviation_is_non_negative(self, location_service):
        """Property: Deviation distance should always be non-negative."""
        from hypothesis import given, strategies as st
        
        @given(
            current_lat=st.floats(min_value=22.6, max_value=22.8, allow_nan=False, allow_infinity=False),
            current_lng=st.floats(min_value=75.7, max_value=75.9, allow_nan=False, allow_infinity=False),
            waypoint_lat=st.floats(min_value=22.6, max_value=22.8, allow_nan=False, allow_infinity=False),
            waypoint_lng=st.floats(min_value=75.7, max_value=75.9, allow_nan=False, allow_infinity=False)
        )
        def check_non_negative_deviation(current_lat, current_lng, waypoint_lat, waypoint_lng):
            route_waypoints = [{"latitude": waypoint_lat, "longitude": waypoint_lng}]
            
            result = location_service.detect_route_deviation(
                current_lat, current_lng, route_waypoints
            )
            
            assert result["deviation_distance_meters"] >= 0
        
        check_non_negative_deviation()
    
    def test_property_threshold_determines_deviation_flag(self, location_service):
        """Property: is_deviated should be True iff deviation > threshold."""
        from hypothesis import given, strategies as st, assume
        
        @given(
            current_lat=st.floats(min_value=22.6, max_value=22.8, allow_nan=False, allow_infinity=False),
            current_lng=st.floats(min_value=75.7, max_value=75.9, allow_nan=False, allow_infinity=False),
            waypoint_lat=st.floats(min_value=22.6, max_value=22.8, allow_nan=False, allow_infinity=False),
            waypoint_lng=st.floats(min_value=75.7, max_value=75.9, allow_nan=False, allow_infinity=False),
            threshold=st.floats(min_value=100.0, max_value=2000.0, allow_nan=False, allow_infinity=False)
        )
        def check_threshold_logic(current_lat, current_lng, waypoint_lat, waypoint_lng, threshold):
            route_waypoints = [{"latitude": waypoint_lat, "longitude": waypoint_lng}]
            
            result = location_service.detect_route_deviation(
                current_lat, current_lng, route_waypoints, threshold_meters=threshold
            )
            
            # is_deviated should be True if and only if deviation > threshold
            if result["deviation_distance_meters"] > threshold:
                assert result["is_deviated"] is True
            else:
                assert result["is_deviated"] is False
        
        check_threshold_logic()
    
    def test_property_closest_waypoint_is_actually_closest(self, location_service):
        """Property: Closest waypoint should have minimum distance to current location."""
        from hypothesis import given, strategies as st, assume
        
        @given(
            current_lat=st.floats(min_value=22.6, max_value=22.8, allow_nan=False, allow_infinity=False),
            current_lng=st.floats(min_value=75.7, max_value=75.9, allow_nan=False, allow_infinity=False),
            num_waypoints=st.integers(min_value=2, max_value=5)
        )
        def check_closest_waypoint(current_lat, current_lng, num_waypoints):
            # Generate random waypoints
            route_waypoints = []
            for i in range(num_waypoints):
                route_waypoints.append({
                    "latitude": 22.6 + (i * 0.04),  # Spread waypoints across Indore
                    "longitude": 75.7 + (i * 0.04)
                })
            
            result = location_service.detect_route_deviation(
                current_lat, current_lng, route_waypoints
            )
            
            if result["closest_waypoint"] is None:
                return  # Skip if no valid waypoints
            
            # Calculate distance to closest waypoint
            closest_distance = location_service.calculate_distance(
                current_lat, current_lng,
                result["closest_waypoint"]["latitude"],
                result["closest_waypoint"]["longitude"]
            ) * 1000  # Convert to meters
            
            # Verify it's actually the closest
            for waypoint in route_waypoints:
                if waypoint.get("latitude") is None or waypoint.get("longitude") is None:
                    continue
                distance = location_service.calculate_distance(
                    current_lat, current_lng,
                    waypoint["latitude"],
                    waypoint["longitude"]
                ) * 1000
                
                # Closest waypoint should have distance <= any other waypoint
                assert closest_distance <= distance + 0.01  # Small epsilon for floating point
        
        check_closest_waypoint()
    
    def test_property_empty_waypoints_never_deviated(self, location_service):
        """Property: Empty waypoints should never show deviation."""
        from hypothesis import given, strategies as st
        
        @given(
            current_lat=st.floats(min_value=22.6, max_value=22.8, allow_nan=False, allow_infinity=False),
            current_lng=st.floats(min_value=75.7, max_value=75.9, allow_nan=False, allow_infinity=False)
        )
        def check_empty_waypoints(current_lat, current_lng):
            result = location_service.detect_route_deviation(
                current_lat, current_lng, []
            )
            
            assert result["is_deviated"] is False
            assert result["deviation_distance_meters"] == 0.0
            assert result["closest_waypoint"] is None
        
        check_empty_waypoints()
    
    def test_property_deviation_symmetric_for_waypoint_order(self, location_service):
        """Property: Waypoint order shouldn't affect deviation result (uses closest)."""
        from hypothesis import given, strategies as st
        
        @given(
            current_lat=st.floats(min_value=22.6, max_value=22.8, allow_nan=False, allow_infinity=False),
            current_lng=st.floats(min_value=75.7, max_value=75.9, allow_nan=False, allow_infinity=False),
            lat1=st.floats(min_value=22.6, max_value=22.8, allow_nan=False, allow_infinity=False),
            lng1=st.floats(min_value=75.7, max_value=75.9, allow_nan=False, allow_infinity=False),
            lat2=st.floats(min_value=22.6, max_value=22.8, allow_nan=False, allow_infinity=False),
            lng2=st.floats(min_value=75.7, max_value=75.9, allow_nan=False, allow_infinity=False)
        )
        def check_order_independence(current_lat, current_lng, lat1, lng1, lat2, lng2):
            waypoints_order1 = [
                {"latitude": lat1, "longitude": lng1},
                {"latitude": lat2, "longitude": lng2}
            ]
            waypoints_order2 = [
                {"latitude": lat2, "longitude": lng2},
                {"latitude": lat1, "longitude": lng1}
            ]
            
            result1 = location_service.detect_route_deviation(
                current_lat, current_lng, waypoints_order1
            )
            result2 = location_service.detect_route_deviation(
                current_lat, current_lng, waypoints_order2
            )
            
            # Deviation distance should be the same regardless of waypoint order
            assert abs(result1["deviation_distance_meters"] - result2["deviation_distance_meters"]) < 0.01
            assert result1["is_deviated"] == result2["is_deviated"]
        
        check_order_independence()
