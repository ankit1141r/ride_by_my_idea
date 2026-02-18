"""
Tests for the Rating model.
"""
import pytest
from datetime import datetime
from app.models.rating import Rating
from app.models.user import User, UserType
from app.models.ride import Ride, RideStatus, PaymentStatus


def test_rating_model_has_required_fields():
    """Test that Rating model has all required fields from the design."""
    rating = Rating()
    
    # Check that all required attributes exist
    assert hasattr(rating, 'rating_id')
    assert hasattr(rating, 'ride_id')
    assert hasattr(rating, 'rater_id')
    assert hasattr(rating, 'ratee_id')
    assert hasattr(rating, 'stars')
    assert hasattr(rating, 'review')
    assert hasattr(rating, 'created_at')


def test_create_rating_with_valid_stars(db_session):
    """Test creating a rating with valid star values (1-5)."""
    # Create test users
    rider = User(
        user_id="rider-1",
        phone_number="+919876543210",
        phone_verified=True,
        name="Test Rider",
        email="rider@test.com",
        user_type=UserType.RIDER,
        password_hash="hashed_password"
    )
    driver = User(
        user_id="driver-1",
        phone_number="+919876543211",
        phone_verified=True,
        name="Test Driver",
        email="driver@test.com",
        user_type=UserType.DRIVER,
        password_hash="hashed_password"
    )
    
    # Create test ride
    ride = Ride(
        ride_id="ride-1",
        rider_id="rider-1",
        driver_id="driver-1",
        status=RideStatus.COMPLETED,
        pickup_location={"lat": 22.7, "lon": 75.8, "address": "Pickup"},
        destination={"lat": 22.71, "lon": 75.81, "address": "Destination"},
        estimated_fare=100.0,
        fare_breakdown={"base": 30, "distance": 70},
        payment_status=PaymentStatus.COMPLETED
    )
    
    db_session.add_all([rider, driver, ride])
    db_session.commit()
    
    # Test valid star values
    for stars in range(1, 6):
        rating = Rating(
            rating_id=f"rating-{stars}",
            ride_id="ride-1",
            rater_id="rider-1",
            ratee_id="driver-1",
            stars=stars,
            review=f"Test review with {stars} stars"
        )
        db_session.add(rating)
        db_session.commit()
        
        # Verify rating was created
        saved_rating = db_session.query(Rating).filter_by(rating_id=f"rating-{stars}").first()
        assert saved_rating is not None
        assert saved_rating.stars == stars
        assert saved_rating.review == f"Test review with {stars} stars"


def test_rating_without_review(db_session):
    """Test creating a rating without a review text."""
    # Create test users
    rider = User(
        user_id="rider-2",
        phone_number="+919876543212",
        phone_verified=True,
        name="Test Rider 2",
        email="rider2@test.com",
        user_type=UserType.RIDER,
        password_hash="hashed_password"
    )
    driver = User(
        user_id="driver-2",
        phone_number="+919876543213",
        phone_verified=True,
        name="Test Driver 2",
        email="driver2@test.com",
        user_type=UserType.DRIVER,
        password_hash="hashed_password"
    )
    
    # Create test ride
    ride = Ride(
        ride_id="ride-2",
        rider_id="rider-2",
        driver_id="driver-2",
        status=RideStatus.COMPLETED,
        pickup_location={"lat": 22.7, "lon": 75.8, "address": "Pickup"},
        destination={"lat": 22.71, "lon": 75.81, "address": "Destination"},
        estimated_fare=100.0,
        fare_breakdown={"base": 30, "distance": 70},
        payment_status=PaymentStatus.COMPLETED
    )
    
    db_session.add_all([rider, driver, ride])
    db_session.commit()
    
    # Create rating without review
    rating = Rating(
        rating_id="rating-no-review",
        ride_id="ride-2",
        rater_id="rider-2",
        ratee_id="driver-2",
        stars=4
    )
    db_session.add(rating)
    db_session.commit()
    
    # Verify rating was created without review
    saved_rating = db_session.query(Rating).filter_by(rating_id="rating-no-review").first()
    assert saved_rating is not None
    assert saved_rating.stars == 4
    assert saved_rating.review is None


def test_rating_has_timestamp(db_session):
    """Test that rating has a created_at timestamp."""
    # Create test users
    rider = User(
        user_id="rider-4",
        phone_number="+919876543216",
        phone_verified=True,
        name="Test Rider 4",
        email="rider4@test.com",
        user_type=UserType.RIDER,
        password_hash="hashed_password"
    )
    driver = User(
        user_id="driver-4",
        phone_number="+919876543217",
        phone_verified=True,
        name="Test Driver 4",
        email="driver4@test.com",
        user_type=UserType.DRIVER,
        password_hash="hashed_password"
    )
    
    # Create test ride
    ride = Ride(
        ride_id="ride-4",
        rider_id="rider-4",
        driver_id="driver-4",
        status=RideStatus.COMPLETED,
        pickup_location={"lat": 22.7, "lon": 75.8, "address": "Pickup"},
        destination={"lat": 22.71, "lon": 75.81, "address": "Destination"},
        estimated_fare=100.0,
        fare_breakdown={"base": 30, "distance": 70},
        payment_status=PaymentStatus.COMPLETED
    )
    
    db_session.add_all([rider, driver, ride])
    db_session.commit()
    
    # Create rating
    before_time = datetime.utcnow()
    rating = Rating(
        rating_id="rating-timestamp",
        ride_id="ride-4",
        rater_id="rider-4",
        ratee_id="driver-4",
        stars=3
    )
    db_session.add(rating)
    db_session.commit()
    after_time = datetime.utcnow()
    
    # Verify timestamp is set
    saved_rating = db_session.query(Rating).filter_by(rating_id="rating-timestamp").first()
    assert saved_rating is not None
    assert saved_rating.created_at is not None
    assert before_time <= saved_rating.created_at <= after_time


def test_rating_foreign_keys(db_session):
    """Test that rating properly links to ride and users."""
    # Create test users
    rider = User(
        user_id="rider-5",
        phone_number="+919876543218",
        phone_verified=True,
        name="Test Rider 5",
        email="rider5@test.com",
        user_type=UserType.RIDER,
        password_hash="hashed_password"
    )
    driver = User(
        user_id="driver-5",
        phone_number="+919876543219",
        phone_verified=True,
        name="Test Driver 5",
        email="driver5@test.com",
        user_type=UserType.DRIVER,
        password_hash="hashed_password"
    )
    
    # Create test ride
    ride = Ride(
        ride_id="ride-5",
        rider_id="rider-5",
        driver_id="driver-5",
        status=RideStatus.COMPLETED,
        pickup_location={"lat": 22.7, "lon": 75.8, "address": "Pickup"},
        destination={"lat": 22.71, "lon": 75.81, "address": "Destination"},
        estimated_fare=100.0,
        fare_breakdown={"base": 30, "distance": 70},
        payment_status=PaymentStatus.COMPLETED
    )
    
    db_session.add_all([rider, driver, ride])
    db_session.commit()
    
    # Create rating
    rating = Rating(
        rating_id="rating-fk",
        ride_id="ride-5",
        rater_id="rider-5",
        ratee_id="driver-5",
        stars=4
    )
    db_session.add(rating)
    db_session.commit()
    
    # Verify foreign keys are correct
    saved_rating = db_session.query(Rating).filter_by(rating_id="rating-fk").first()
    assert saved_rating.ride_id == "ride-5"
    assert saved_rating.rater_id == "rider-5"
    assert saved_rating.ratee_id == "driver-5"
