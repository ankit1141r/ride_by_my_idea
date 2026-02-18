"""
Unit tests for ride request creation endpoint.

Tests Requirements: 2.1, 2.2, 2.4, 2.5
"""
import pytest
from fastapi import status
from datetime import datetime
from unittest.mock import Mock, patch, AsyncMock
from sqlalchemy.orm import Session

from app.routers.rides import create_ride_request
from app.schemas.ride import RideRequestCreate, LocationInput
from app.models.ride import Ride, RideStatus, PaymentStatus
from app.services.location_service import LocationService
from app.services.fare_service import calculate_estimated_fare


@pytest.fixture
def mock_db():
    """Mock database session."""
    db = Mock(spec=Session)
    db.add = Mock()
    db.commit = Mock()
    db.refresh = Mock()
    return db


@pytest.fixture
def mock_mongodb():
    """Mock MongoDB database."""
    mock_db = Mock()
    # Make the mock subscriptable to support db[collection_name]
    mock_collection = Mock()
    mock_db.__getitem__ = Mock(return_value=mock_collection)
    return mock_db


@pytest.fixture
def mock_current_user_rider():
    """Mock authenticated rider user."""
    return {
        "user_id": "rider_123",
        "user_type": "rider",
        "phone_verified": True
    }


@pytest.fixture
def mock_current_user_driver():
    """Mock authenticated driver user."""
    return {
        "user_id": "driver_123",
        "user_type": "driver",
        "phone_verified": True
    }


@pytest.fixture
def valid_ride_request():
    """Valid ride request within Indore boundaries."""
    return RideRequestCreate(
        pickup_location=LocationInput(
            latitude=22.7196,
            longitude=75.8577,
            address="Vijay Nagar, Indore, Madhya Pradesh"
        ),
        destination=LocationInput(
            latitude=22.7520,
            longitude=75.8937,
            address="Rajwada, Indore, Madhya Pradesh"
        )
    )


@pytest.fixture
def ride_request_pickup_outside_boundary():
    """Ride request with pickup outside Indore boundaries."""
    return RideRequestCreate(
        pickup_location=LocationInput(
            latitude=23.0,  # Outside Indore boundary
            longitude=76.0,
            address="Outside Indore"
        ),
        destination=LocationInput(
            latitude=22.7520,
            longitude=75.8937,
            address="Rajwada, Indore, Madhya Pradesh"
        )
    )


@pytest.fixture
def ride_request_destination_outside_boundary():
    """Ride request with destination outside Indore boundaries."""
    return RideRequestCreate(
        pickup_location=LocationInput(
            latitude=22.7196,
            longitude=75.8577,
            address="Vijay Nagar, Indore, Madhya Pradesh"
        ),
        destination=LocationInput(
            latitude=23.0,  # Outside Indore boundary
            longitude=76.0,
            address="Outside Indore"
        )
    )


class TestRideRequestCreation:
    """Test suite for ride request creation endpoint."""
    
    @pytest.mark.asyncio
    async def test_create_valid_ride_request(
        self,
        valid_ride_request,
        mock_db,
        mock_mongodb,
        mock_current_user_rider
    ):
        """
        Test creating a valid ride request within boundaries.
        
        Requirements: 2.1, 2.2
        """
        # Mock the ride object that will be added to db
        def mock_refresh(ride):
            ride.ride_id = "ride_test123"
            ride.requested_at = datetime.utcnow()
        
        mock_db.refresh.side_effect = mock_refresh
        
        # Call the endpoint
        response = await create_ride_request(
            ride_request=valid_ride_request,
            db=mock_db,
            mongodb=mock_mongodb,
            current_user=mock_current_user_rider
        )
        
        # Verify response
        assert response.request_id.startswith("ride_")
        assert response.estimated_fare > 0
        assert response.estimated_arrival > 0
        assert response.status == "requested"
        assert response.message == "Ride request created successfully"
        
        # Verify fare breakdown
        assert response.fare_breakdown.base == 30.0
        assert response.fare_breakdown.per_km == 12.0
        assert response.fare_breakdown.distance > 0
        assert response.fare_breakdown.surge == 1.0
        
        # Verify locations
        assert response.pickup_location["latitude"] == 22.7196
        assert response.pickup_location["longitude"] == 75.8577
        assert response.destination["latitude"] == 22.7520
        assert response.destination["longitude"] == 75.8937
        
        # Verify database operations
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_reject_pickup_outside_boundary(
        self,
        ride_request_pickup_outside_boundary,
        mock_db,
        mock_mongodb,
        mock_current_user_rider
    ):
        """
        Test that ride request is rejected when pickup is outside Indore boundaries.
        
        Requirements: 2.4
        """
        from fastapi import HTTPException
        
        # Call the endpoint and expect an exception
        with pytest.raises(HTTPException) as exc_info:
            await create_ride_request(
                ride_request=ride_request_pickup_outside_boundary,
                db=mock_db,
                mongodb=mock_mongodb,
                current_user=mock_current_user_rider
            )
        
        # Verify exception details
        assert exc_info.value.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert "boundary_violation" in str(exc_info.value.detail)
        assert "pickup" in str(exc_info.value.detail)
        
        # Verify no database operations occurred
        mock_db.add.assert_not_called()
        mock_db.commit.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_reject_destination_outside_boundary(
        self,
        ride_request_destination_outside_boundary,
        mock_db,
        mock_mongodb,
        mock_current_user_rider
    ):
        """
        Test that ride request is rejected when destination is outside Indore boundaries.
        
        Requirements: 2.4
        """
        from fastapi import HTTPException
        
        # Call the endpoint and expect an exception
        with pytest.raises(HTTPException) as exc_info:
            await create_ride_request(
                ride_request=ride_request_destination_outside_boundary,
                db=mock_db,
                mongodb=mock_mongodb,
                current_user=mock_current_user_rider
            )
        
        # Verify exception details
        assert exc_info.value.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert "boundary_violation" in str(exc_info.value.detail)
        assert "destination" in str(exc_info.value.detail)
        
        # Verify no database operations occurred
        mock_db.add.assert_not_called()
        mock_db.commit.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_driver_cannot_create_ride_request(
        self,
        valid_ride_request,
        mock_db,
        mock_mongodb,
        mock_current_user_driver
    ):
        """
        Test that drivers cannot create ride requests.
        
        Requirements: 2.1
        """
        from fastapi import HTTPException
        
        # Call the endpoint and expect an exception
        with pytest.raises(HTTPException) as exc_info:
            await create_ride_request(
                ride_request=valid_ride_request,
                db=mock_db,
                mongodb=mock_mongodb,
                current_user=mock_current_user_driver
            )
        
        # Verify exception details
        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
        assert "Only riders can create ride requests" in str(exc_info.value.detail)
        
        # Verify no database operations occurred
        mock_db.add.assert_not_called()
        mock_db.commit.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_fare_calculation_accuracy(
        self,
        valid_ride_request,
        mock_db,
        mock_mongodb,
        mock_current_user_rider
    ):
        """
        Test that fare is calculated correctly based on distance.
        
        Requirements: 2.2, 5.1, 5.2
        """
        # Mock the ride object that will be added to db
        def mock_refresh(ride):
            ride.ride_id = "ride_test123"
            ride.requested_at = datetime.utcnow()
        
        mock_db.refresh.side_effect = mock_refresh
        
        # Call the endpoint
        response = await create_ride_request(
            ride_request=valid_ride_request,
            db=mock_db,
            mongodb=mock_mongodb,
            current_user=mock_current_user_rider
        )
        
        # Calculate expected fare manually
        # Distance between (22.7196, 75.8577) and (22.7520, 75.8937) is approximately 5.5 km
        expected_distance = response.fare_breakdown.distance
        expected_fare = 30.0 + (expected_distance * 12.0)
        
        # Verify fare calculation
        assert abs(response.estimated_fare - expected_fare) < 0.01
        assert response.fare_breakdown.base == 30.0
        assert response.fare_breakdown.per_km == 12.0
    
    @pytest.mark.asyncio
    async def test_estimated_arrival_time_provided(
        self,
        valid_ride_request,
        mock_db,
        mock_mongodb,
        mock_current_user_rider
    ):
        """
        Test that estimated arrival time is provided in response.
        
        Requirements: 2.5
        """
        # Mock the ride object that will be added to db
        def mock_refresh(ride):
            ride.ride_id = "ride_test123"
            ride.requested_at = datetime.utcnow()
        
        mock_db.refresh.side_effect = mock_refresh
        
        # Call the endpoint
        response = await create_ride_request(
            ride_request=valid_ride_request,
            db=mock_db,
            mongodb=mock_mongodb,
            current_user=mock_current_user_rider
        )
        
        # Verify estimated arrival is provided and reasonable
        assert response.estimated_arrival > 0
        assert response.estimated_arrival < 60  # Should be less than 60 minutes for intra-city
    
    @pytest.mark.asyncio
    async def test_ride_record_created_with_correct_status(
        self,
        valid_ride_request,
        mock_db,
        mock_mongodb,
        mock_current_user_rider
    ):
        """
        Test that ride record is created with REQUESTED status.
        
        Requirements: 2.1
        """
        # Mock the ride object that will be added to db
        def mock_refresh(ride):
            ride.ride_id = "ride_test123"
            ride.requested_at = datetime.utcnow()
        
        mock_db.refresh.side_effect = mock_refresh
        
        # Call the endpoint
        response = await create_ride_request(
            ride_request=valid_ride_request,
            db=mock_db,
            mongodb=mock_mongodb,
            current_user=mock_current_user_rider
        )
        
        # Verify the ride object added to database
        mock_db.add.assert_called_once()
        ride_added = mock_db.add.call_args[0][0]
        
        assert isinstance(ride_added, Ride)
        assert ride_added.status == RideStatus.REQUESTED
        assert ride_added.rider_id == "rider_123"
        assert ride_added.payment_status == PaymentStatus.PENDING
        assert ride_added.driver_id is None


class TestFareBreakdownInResponse:
    """Test suite for fare breakdown in response."""
    
    @pytest.mark.asyncio
    async def test_fare_breakdown_includes_all_components(
        self,
        valid_ride_request,
        mock_db,
        mock_mongodb,
        mock_current_user_rider
    ):
        """
        Test that fare breakdown includes base, per_km, distance, and surge.
        
        Requirements: 2.2, 5.3
        """
        # Mock the ride object that will be added to db
        def mock_refresh(ride):
            ride.ride_id = "ride_test123"
            ride.requested_at = datetime.utcnow()
        
        mock_db.refresh.side_effect = mock_refresh
        
        # Call the endpoint
        response = await create_ride_request(
            ride_request=valid_ride_request,
            db=mock_db,
            mongodb=mock_mongodb,
            current_user=mock_current_user_rider
        )
        
        # Verify all fare breakdown components are present
        assert hasattr(response.fare_breakdown, 'base')
        assert hasattr(response.fare_breakdown, 'per_km')
        assert hasattr(response.fare_breakdown, 'distance')
        assert hasattr(response.fare_breakdown, 'surge')
        
        # Verify values are reasonable
        assert response.fare_breakdown.base == 30.0
        assert response.fare_breakdown.per_km == 12.0
        assert response.fare_breakdown.distance > 0
        assert response.fare_breakdown.surge == 1.0


class TestEdgeCases:
    """Test suite for edge cases."""
    
    @pytest.mark.asyncio
    async def test_zero_distance_ride(
        self,
        mock_db,
        mock_mongodb,
        mock_current_user_rider
    ):
        """
        Test ride request with same pickup and destination (zero distance).
        
        Requirements: 2.2, 5.1
        """
        # Create ride request with same pickup and destination
        same_location_request = RideRequestCreate(
            pickup_location=LocationInput(
                latitude=22.7196,
                longitude=75.8577,
                address="Vijay Nagar, Indore, Madhya Pradesh"
            ),
            destination=LocationInput(
                latitude=22.7196,
                longitude=75.8577,
                address="Vijay Nagar, Indore, Madhya Pradesh"
            )
        )
        
        # Mock the ride object that will be added to db
        def mock_refresh(ride):
            ride.ride_id = "ride_test123"
            ride.requested_at = datetime.utcnow()
        
        mock_db.refresh.side_effect = mock_refresh
        
        # Call the endpoint
        response = await create_ride_request(
            ride_request=same_location_request,
            db=mock_db,
            mongodb=mock_mongodb,
            current_user=mock_current_user_rider
        )
        
        # Verify fare is at least base fare
        assert response.estimated_fare >= 30.0
        assert response.fare_breakdown.distance < 0.1  # Very small distance
    
    @pytest.mark.asyncio
    async def test_boundary_edge_location(
        self,
        mock_db,
        mock_mongodb,
        mock_current_user_rider
    ):
        """
        Test ride request with location exactly at boundary edge.
        
        Requirements: 2.4
        """
        # Create ride request with location at boundary edge
        boundary_request = RideRequestCreate(
            pickup_location=LocationInput(
                latitude=22.6,  # Exactly at min boundary
                longitude=75.7,  # Exactly at min boundary
                address="Boundary Location, Indore"
            ),
            destination=LocationInput(
                latitude=22.8,  # Exactly at max boundary
                longitude=75.9,  # Exactly at max boundary
                address="Boundary Location, Indore"
            )
        )
        
        # Mock the ride object that will be added to db
        def mock_refresh(ride):
            ride.ride_id = "ride_test123"
            ride.requested_at = datetime.utcnow()
        
        mock_db.refresh.side_effect = mock_refresh
        
        # Call the endpoint - should succeed as boundaries are inclusive
        response = await create_ride_request(
            ride_request=boundary_request,
            db=mock_db,
            mongodb=mock_mongodb,
            current_user=mock_current_user_rider
        )
        
        # Verify request was created successfully
        assert response.request_id.startswith("ride_")
        assert response.status == "requested"
