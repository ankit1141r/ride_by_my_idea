"""
Unit tests for ride history endpoints.

Tests Requirements: 9.1, 9.2, 9.3, 9.4, 9.5
"""
import pytest
from fastapi import status, HTTPException
from datetime import datetime, timedelta
from unittest.mock import Mock, MagicMock
from sqlalchemy.orm import Session

from app.routers.rides import get_ride_history, get_ride_details
from app.models.ride import Ride, RideStatus, PaymentStatus


@pytest.fixture
def mock_db():
    """Mock database session."""
    db = Mock(spec=Session)
    return db


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
        "user_id": "driver_456",
        "user_type": "driver",
        "phone_verified": True
    }


@pytest.fixture
def sample_completed_ride():
    """Sample completed ride."""
    return Ride(
        ride_id="ride_001",
        rider_id="rider_123",
        driver_id="driver_456",
        status=RideStatus.COMPLETED,
        pickup_location={
            "latitude": 22.7196,
            "longitude": 75.8577,
            "address": "Vijay Nagar, Indore"
        },
        destination={
            "latitude": 22.7520,
            "longitude": 75.8937,
            "address": "Rajwada, Indore"
        },
        requested_at=datetime(2024, 1, 15, 10, 30),
        matched_at=datetime(2024, 1, 15, 10, 32),
        pickup_time=datetime(2024, 1, 15, 10, 40),
        start_time=datetime(2024, 1, 15, 10, 42),
        completed_at=datetime(2024, 1, 15, 11, 0),
        estimated_fare=96.0,
        final_fare=96.0,
        fare_breakdown={
            "base": 30.0,
            "per_km": 12.0,
            "distance": 5.5,
            "surge": 1.0,
            "total": 96.0
        },
        payment_status=PaymentStatus.COMPLETED,
        transaction_id="txn_xyz789",
        driver_rating=5,
        rider_rating=4,
        driver_review="Great passenger",
        rider_review="Good driver"
    )


@pytest.fixture
def sample_requested_ride():
    """Sample requested ride (not yet matched)."""
    return Ride(
        ride_id="ride_002",
        rider_id="rider_123",
        driver_id=None,
        status=RideStatus.REQUESTED,
        pickup_location={
            "latitude": 22.7196,
            "longitude": 75.8577,
            "address": "Vijay Nagar, Indore"
        },
        destination={
            "latitude": 22.7520,
            "longitude": 75.8937,
            "address": "Rajwada, Indore"
        },
        requested_at=datetime(2024, 1, 16, 14, 0),
        estimated_fare=90.0,
        fare_breakdown={
            "base": 30.0,
            "per_km": 12.0,
            "distance": 5.0,
            "surge": 1.0,
            "total": 90.0
        },
        payment_status=PaymentStatus.PENDING
    )


@pytest.fixture
def sample_cancelled_ride():
    """Sample cancelled ride."""
    return Ride(
        ride_id="ride_003",
        rider_id="rider_123",
        driver_id="driver_456",
        status=RideStatus.CANCELLED,
        pickup_location={
            "latitude": 22.7196,
            "longitude": 75.8577,
            "address": "Vijay Nagar, Indore"
        },
        destination={
            "latitude": 22.7520,
            "longitude": 75.8937,
            "address": "Rajwada, Indore"
        },
        requested_at=datetime(2024, 1, 14, 9, 0),
        matched_at=datetime(2024, 1, 14, 9, 2),
        estimated_fare=96.0,
        fare_breakdown={
            "base": 30.0,
            "per_km": 12.0,
            "distance": 5.5,
            "surge": 1.0,
            "total": 96.0
        },
        payment_status=PaymentStatus.PENDING,
        cancelled_by="rider_123",
        cancellation_reason="Changed plans",
        cancellation_fee=20.0,
        cancellation_timestamp=datetime(2024, 1, 14, 9, 5)
    )


class TestRideHistory:
    """Test suite for ride history endpoint."""
    
    @pytest.mark.asyncio
    async def test_get_ride_history_for_rider(
        self,
        mock_db,
        mock_current_user_rider,
        sample_completed_ride,
        sample_requested_ride,
        sample_cancelled_ride
    ):
        """
        Test getting ride history for a rider.
        
        Requirements: 9.1, 9.2, 9.3
        """
        # Mock query chain
        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        
        # Return rides in reverse chronological order
        mock_query.all.return_value = [
            sample_requested_ride,  # Most recent
            sample_completed_ride,
            sample_cancelled_ride   # Oldest
        ]
        
        # Call endpoint
        response = await get_ride_history(
            start_date=None,
            end_date=None,
            db=mock_db,
            current_user=mock_current_user_rider
        )
        
        # Verify response structure
        assert len(response.rides) == 3
        assert response.total == 3
        
        # Verify rides are in reverse chronological order (Requirement 9.2)
        assert response.rides[0].ride_id == "ride_002"
        assert response.rides[1].ride_id == "ride_001"
        assert response.rides[2].ride_id == "ride_003"
        
        # Verify required fields are present (Requirement 9.3)
        first_ride = response.rides[0]
        assert first_ride.ride_id is not None
        assert first_ride.date is not None
        assert first_ride.pickup_location is not None
        assert first_ride.destination is not None
        assert first_ride.fare is not None
        assert first_ride.status is not None
    
    @pytest.mark.asyncio
    async def test_get_ride_history_for_driver(
        self,
        mock_db,
        mock_current_user_driver,
        sample_completed_ride
    ):
        """
        Test getting ride history for a driver.
        
        Requirements: 9.1
        """
        # Mock query chain
        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = [sample_completed_ride]
        
        # Call endpoint
        response = await get_ride_history(
            start_date=None,
            end_date=None,
            db=mock_db,
            current_user=mock_current_user_driver
        )
        
        # Verify response
        assert len(response.rides) == 1
        assert response.rides[0].ride_id == "ride_001"
        assert response.rides[0].rider_rating == 4  # Driver sees rider rating
        assert response.rides[0].driver_rating is None  # Driver doesn't see their own rating in list
    
    @pytest.mark.asyncio
    async def test_filter_by_date_range(
        self,
        mock_db,
        mock_current_user_rider,
        sample_completed_ride
    ):
        """
        Test filtering ride history by date range.
        
        Requirements: 9.4
        """
        # Mock query chain
        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = [sample_completed_ride]
        
        # Call endpoint with date filters
        start_date = datetime(2024, 1, 15, 0, 0)
        end_date = datetime(2024, 1, 15, 23, 59)
        
        response = await get_ride_history(
            start_date=start_date,
            end_date=end_date,
            db=mock_db,
            current_user=mock_current_user_rider
        )
        
        # Verify filters were applied
        assert mock_query.filter.call_count >= 1
        
        # Verify response
        assert len(response.rides) == 1
        assert response.rides[0].ride_id == "ride_001"
    
    @pytest.mark.asyncio
    async def test_empty_ride_history(
        self,
        mock_db,
        mock_current_user_rider
    ):
        """
        Test getting ride history when user has no rides.
        
        Requirements: 9.1
        """
        # Mock query chain
        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []
        
        # Call endpoint
        response = await get_ride_history(
            start_date=None,
            end_date=None,
            db=mock_db,
            current_user=mock_current_user_rider
        )
        
        # Verify empty response
        assert len(response.rides) == 0
        assert response.total == 0
    
    @pytest.mark.asyncio
    async def test_ride_history_shows_correct_fare(
        self,
        mock_db,
        mock_current_user_rider,
        sample_completed_ride,
        sample_requested_ride
    ):
        """
        Test that ride history shows final fare for completed rides and estimated for others.
        
        Requirements: 9.3
        """
        # Mock query chain
        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = [sample_completed_ride, sample_requested_ride]
        
        # Call endpoint
        response = await get_ride_history(
            start_date=None,
            end_date=None,
            db=mock_db,
            current_user=mock_current_user_rider
        )
        
        # Verify completed ride shows final fare
        completed = next(r for r in response.rides if r.ride_id == "ride_001")
        assert completed.fare == 96.0  # final_fare
        
        # Verify requested ride shows estimated fare
        requested = next(r for r in response.rides if r.ride_id == "ride_002")
        assert requested.fare == 90.0  # estimated_fare


class TestRideDetails:
    """Test suite for ride details endpoint."""
    
    @pytest.mark.asyncio
    async def test_get_ride_details_as_rider(
        self,
        mock_db,
        mock_current_user_rider,
        sample_completed_ride
    ):
        """
        Test getting detailed ride information as the rider.
        
        Requirements: 9.3, 9.5
        """
        # Mock query
        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = sample_completed_ride
        
        # Call endpoint
        response = await get_ride_details(
            ride_id="ride_001",
            db=mock_db,
            current_user=mock_current_user_rider
        )
        
        # Verify all required fields are present (Requirement 9.5)
        assert response.ride_id == "ride_001"
        assert response.rider_id == "rider_123"
        assert response.driver_id == "driver_456"
        assert response.status == "completed"
        assert response.pickup_location is not None
        assert response.destination is not None
        assert response.requested_at is not None
        assert response.matched_at is not None
        assert response.pickup_time is not None
        assert response.start_time is not None
        assert response.completed_at is not None
        assert response.estimated_fare == 96.0
        assert response.final_fare == 96.0
        assert response.fare_breakdown is not None
        assert response.payment_status == "completed"
        assert response.transaction_id == "txn_xyz789"
        assert response.driver_rating == 5
        assert response.rider_rating == 4
    
    @pytest.mark.asyncio
    async def test_get_ride_details_as_driver(
        self,
        mock_db,
        mock_current_user_driver,
        sample_completed_ride
    ):
        """
        Test getting detailed ride information as the driver.
        
        Requirements: 9.3, 9.5
        """
        # Mock query
        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = sample_completed_ride
        
        # Call endpoint
        response = await get_ride_details(
            ride_id="ride_001",
            db=mock_db,
            current_user=mock_current_user_driver
        )
        
        # Verify response
        assert response.ride_id == "ride_001"
        assert response.driver_id == "driver_456"
    
    @pytest.mark.asyncio
    async def test_get_ride_details_not_found(
        self,
        mock_db,
        mock_current_user_rider
    ):
        """
        Test getting details for non-existent ride.
        
        Requirements: 9.5
        """
        # Mock query returning None
        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None
        
        # Call endpoint and expect exception
        with pytest.raises(HTTPException) as exc_info:
            await get_ride_details(
                ride_id="ride_nonexistent",
                db=mock_db,
                current_user=mock_current_user_rider
            )
        
        # Verify exception
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in str(exc_info.value.detail).lower()
    
    @pytest.mark.asyncio
    async def test_get_ride_details_unauthorized(
        self,
        mock_db,
        sample_completed_ride
    ):
        """
        Test that unauthorized users cannot view ride details.
        
        Requirements: 9.5
        """
        # Mock query
        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = sample_completed_ride
        
        # Create unauthorized user
        unauthorized_user = {
            "user_id": "other_user_789",
            "user_type": "rider",
            "phone_verified": True
        }
        
        # Call endpoint and expect exception
        with pytest.raises(HTTPException) as exc_info:
            await get_ride_details(
                ride_id="ride_001",
                db=mock_db,
                current_user=unauthorized_user
            )
        
        # Verify exception
        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
        assert "not authorized" in str(exc_info.value.detail).lower()
    
    @pytest.mark.asyncio
    async def test_get_ride_details_includes_cancellation_info(
        self,
        mock_db,
        mock_current_user_rider,
        sample_cancelled_ride
    ):
        """
        Test that ride details include cancellation information when applicable.
        
        Requirements: 9.5
        """
        # Mock query
        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = sample_cancelled_ride
        
        # Call endpoint
        response = await get_ride_details(
            ride_id="ride_003",
            db=mock_db,
            current_user=mock_current_user_rider
        )
        
        # Verify cancellation information is included
        assert response.status == "cancelled"
        assert response.cancelled_by == "rider_123"
        assert response.cancellation_reason == "Changed plans"
        assert response.cancellation_fee == 20.0
    
    @pytest.mark.asyncio
    async def test_get_ride_details_includes_route_map(
        self,
        mock_db,
        mock_current_user_rider,
        sample_completed_ride
    ):
        """
        Test that ride details include route map for completed rides.
        
        Requirements: 9.5
        """
        # Add actual route to sample ride
        sample_completed_ride.actual_route = [
            {"latitude": 22.7196, "longitude": 75.8577},
            {"latitude": 22.7300, "longitude": 75.8700},
            {"latitude": 22.7520, "longitude": 75.8937}
        ]
        
        # Mock query
        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = sample_completed_ride
        
        # Call endpoint
        response = await get_ride_details(
            ride_id="ride_001",
            db=mock_db,
            current_user=mock_current_user_rider
        )
        
        # Verify route is included
        assert response.actual_route is not None
        assert len(response.actual_route) == 3


class TestRideHistoryEdgeCases:
    """Test suite for edge cases in ride history."""
    
    @pytest.mark.asyncio
    async def test_filter_with_only_start_date(
        self,
        mock_db,
        mock_current_user_rider,
        sample_completed_ride
    ):
        """
        Test filtering with only start date (no end date).
        
        Requirements: 9.4
        """
        # Mock query chain
        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = [sample_completed_ride]
        
        # Call endpoint with only start date
        start_date = datetime(2024, 1, 1, 0, 0)
        
        response = await get_ride_history(
            start_date=start_date,
            end_date=None,
            db=mock_db,
            current_user=mock_current_user_rider
        )
        
        # Verify response
        assert len(response.rides) == 1
    
    @pytest.mark.asyncio
    async def test_filter_with_only_end_date(
        self,
        mock_db,
        mock_current_user_rider,
        sample_completed_ride
    ):
        """
        Test filtering with only end date (no start date).
        
        Requirements: 9.4
        """
        # Mock query chain
        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = [sample_completed_ride]
        
        # Call endpoint with only end date
        end_date = datetime(2024, 12, 31, 23, 59)
        
        response = await get_ride_history(
            start_date=None,
            end_date=end_date,
            db=mock_db,
            current_user=mock_current_user_rider
        )
        
        # Verify response
        assert len(response.rides) == 1
