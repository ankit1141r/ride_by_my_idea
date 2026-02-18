"""
Tests for driver availability management.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
from app.main import app
from app.database import Base, get_db, get_redis
from app.models.user import User, DriverProfile
from app.services.matching_service import MatchingService
import fakeredis


# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_driver_availability.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Fake Redis for testing
fake_redis = fakeredis.FakeStrictRedis(decode_responses=True)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


def override_get_redis():
    return fake_redis


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_redis] = override_get_redis

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    fake_redis.flushall()


@pytest.fixture
def test_driver():
    """Create a test driver."""
    db = TestingSessionLocal()
    driver = User(
        user_id="driver123",
        phone_number="+919876543210",
        phone_verified=True,
        name="Test Driver",
        email="driver@test.com",
        password_hash="hashed_password",
        user_type="driver",
        created_at=datetime.utcnow()
    )
    driver_profile = DriverProfile(
        driver_id="driver123",
        license_number="DL1234567890",
        license_verified=True,
        vehicle_registration="MP09AB1234",
        vehicle_make="Toyota",
        vehicle_model="Innova",
        vehicle_color="White",
        vehicle_verified=True,
        insurance_expiry=datetime.utcnow() + timedelta(days=90),
        status="unavailable"
    )
    db.add(driver)
    db.add(driver_profile)
    db.commit()
    db.close()
    return driver


class TestSetDriverAvailable:
    """Tests for setting driver to available status."""
    
    def test_set_driver_available_success(self, test_driver):
        """Test successfully setting driver to available."""
        response = client.post(
            "/api/drivers/availability?driver_id=driver123",
            json={
                "status": "available",
                "latitude": 22.7196,
                "longitude": 75.8577
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "Driver driver123 is now available" in data["message"]
        assert data["location"]["latitude"] == 22.7196
        assert data["location"]["longitude"] == 75.8577
    
    def test_set_driver_available_without_location_fails(self, test_driver):
        """Test that setting available without location fails."""
        response = client.post(
            "/api/drivers/availability?driver_id=driver123",
            json={
                "status": "available"
            }
        )
        
        assert response.status_code == 400
        assert "Latitude and longitude are required" in response.json()["detail"]
    
    def test_set_driver_available_stores_in_redis(self, test_driver):
        """Test that availability is stored in Redis."""
        client.post(
            "/api/drivers/availability?driver_id=driver123",
            json={
                "status": "available",
                "latitude": 22.7196,
                "longitude": 75.8577
            }
        )
        
        # Check Redis
        assert fake_redis.sismember("drivers:available", "driver123")
        availability_data = fake_redis.get("driver:availability:driver123")
        assert availability_data is not None
    
    def test_set_driver_available_updates_database(self, test_driver):
        """Test that driver profile status is updated in database."""
        client.post(
            "/api/drivers/availability?driver_id=driver123",
            json={
                "status": "available",
                "latitude": 22.7196,
                "longitude": 75.8577
            }
        )
        
        # Check database
        db = TestingSessionLocal()
        driver = db.query(User).filter(User.user_id == "driver123").first()
        assert driver.driver_profile.status == "available"
        db.close()


class TestSetDriverUnavailable:
    """Tests for setting driver to unavailable status."""
    
    def test_set_driver_unavailable_success(self, test_driver):
        """Test successfully setting driver to unavailable."""
        # First set available
        client.post(
            "/api/drivers/availability?driver_id=driver123",
            json={
                "status": "available",
                "latitude": 22.7196,
                "longitude": 75.8577
            }
        )
        
        # Then set unavailable
        response = client.post(
            "/api/drivers/availability?driver_id=driver123",
            json={
                "status": "unavailable"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "Driver driver123 is now unavailable" in data["message"]
    
    def test_set_driver_unavailable_removes_from_redis_set(self, test_driver):
        """Test that driver is removed from available set in Redis."""
        # First set available
        client.post(
            "/api/drivers/availability?driver_id=driver123",
            json={
                "status": "available",
                "latitude": 22.7196,
                "longitude": 75.8577
            }
        )
        
        # Then set unavailable
        client.post(
            "/api/drivers/availability?driver_id=driver123",
            json={
                "status": "unavailable"
            }
        )
        
        # Check Redis
        assert not fake_redis.sismember("drivers:available", "driver123")
    
    def test_set_driver_unavailable_updates_database(self, test_driver):
        """Test that driver profile status is updated in database."""
        # First set available
        client.post(
            "/api/drivers/availability?driver_id=driver123",
            json={
                "status": "available",
                "latitude": 22.7196,
                "longitude": 75.8577
            }
        )
        
        # Then set unavailable
        client.post(
            "/api/drivers/availability?driver_id=driver123",
            json={
                "status": "unavailable"
            }
        )
        
        # Check database
        db = TestingSessionLocal()
        driver = db.query(User).filter(User.user_id == "driver123").first()
        assert driver.driver_profile.status == "unavailable"
        db.close()


class TestGetDriverStatus:
    """Tests for getting driver availability status."""
    
    def test_get_driver_status_available(self, test_driver):
        """Test getting status of available driver."""
        # Set driver available
        client.post(
            "/api/drivers/availability?driver_id=driver123",
            json={
                "status": "available",
                "latitude": 22.7196,
                "longitude": 75.8577
            }
        )
        
        # Get status
        response = client.get("/api/drivers/availability/driver123")
        
        assert response.status_code == 200
        data = response.json()
        assert data["driver_id"] == "driver123"
        assert data["status"] == "available"
        assert data["location"]["latitude"] == 22.7196
        assert data["location"]["longitude"] == 75.8577
    
    def test_get_driver_status_unavailable(self, test_driver):
        """Test getting status of unavailable driver."""
        # Set driver unavailable
        client.post(
            "/api/drivers/availability?driver_id=driver123",
            json={
                "status": "unavailable"
            }
        )
        
        # Get status
        response = client.get("/api/drivers/availability/driver123")
        
        assert response.status_code == 200
        data = response.json()
        assert data["driver_id"] == "driver123"
        assert data["status"] == "unavailable"
    
    def test_get_driver_status_not_set(self, test_driver):
        """Test getting status when driver hasn't set availability."""
        response = client.get("/api/drivers/availability/driver123")
        
        assert response.status_code == 404
        assert "Driver status not found" in response.json()["detail"]
    
    def test_get_driver_status_nonexistent_driver(self):
        """Test getting status of non-existent driver."""
        response = client.get("/api/drivers/availability/nonexistent")
        
        assert response.status_code == 404
        assert "Driver not found" in response.json()["detail"]


class TestDriverAvailabilityValidation:
    """Tests for driver availability validation."""
    
    def test_invalid_status_value(self, test_driver):
        """Test that invalid status values are rejected."""
        response = client.post(
            "/api/drivers/availability?driver_id=driver123",
            json={
                "status": "invalid_status",
                "latitude": 22.7196,
                "longitude": 75.8577
            }
        )
        
        assert response.status_code == 400
        assert "Invalid status" in response.json()["detail"]
    
    def test_non_driver_user_cannot_set_availability(self):
        """Test that non-driver users cannot set availability."""
        # Create a rider
        db = TestingSessionLocal()
        rider = User(
            user_id="rider123",
            phone_number="+919876543211",
            phone_verified=True,
            name="Test Rider",
            email="rider@test.com",
            password_hash="hashed_password",
            user_type="rider",
            created_at=datetime.utcnow()
        )
        db.add(rider)
        db.commit()
        db.close()
        
        response = client.post(
            "/api/drivers/availability?driver_id=rider123",
            json={
                "status": "available",
                "latitude": 22.7196,
                "longitude": 75.8577
            }
        )
        
        assert response.status_code == 404
        assert "Driver not found" in response.json()["detail"]


class TestMatchingServiceDirectly:
    """Tests for MatchingService methods directly."""
    
    def test_is_driver_available(self, test_driver):
        """Test checking if driver is available."""
        db = TestingSessionLocal()
        matching_service = MatchingService(fake_redis, db)
        
        # Initially not available
        assert not matching_service.is_driver_available("driver123")
        
        # Set available
        matching_service.set_driver_available("driver123", 22.7196, 75.8577)
        
        # Now available
        assert matching_service.is_driver_available("driver123")
        
        db.close()
    
    def test_set_driver_busy(self, test_driver):
        """Test setting driver to busy status."""
        db = TestingSessionLocal()
        matching_service = MatchingService(fake_redis, db)
        
        # Set available first
        matching_service.set_driver_available("driver123", 22.7196, 75.8577)
        assert matching_service.is_driver_available("driver123")
        
        # Set busy
        result = matching_service.set_driver_busy("driver123")
        
        assert result["status"] == "success"
        assert not matching_service.is_driver_available("driver123")
        
        # Check status
        status = matching_service.get_driver_status("driver123")
        assert status["status"] == "busy"
        
        db.close()
    
    def test_update_driver_location(self, test_driver):
        """Test updating driver location."""
        db = TestingSessionLocal()
        matching_service = MatchingService(fake_redis, db)
        
        # Set initial location
        matching_service.set_driver_available("driver123", 22.7196, 75.8577)
        
        # Update location
        result = matching_service.update_driver_location("driver123", 22.7200, 75.8600)
        
        assert result["status"] == "success"
        assert result["location"]["latitude"] == 22.7200
        assert result["location"]["longitude"] == 75.8600
        
        # Verify updated location
        status = matching_service.get_driver_status("driver123")
        assert status["latitude"] == 22.7200
        assert status["longitude"] == 75.8600
        
        db.close()
