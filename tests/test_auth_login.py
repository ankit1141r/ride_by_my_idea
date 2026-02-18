"""
Unit tests for user login endpoint and JWT token generation.
Tests Requirement 1.8
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
from jose import jwt
import redis

from app.main import app
from app.database import Base, get_db
from app import database
from app.models.user import User, DriverProfile, UserType, DriverStatus
from app.routers.auth import hash_password
from app.config import settings


# Test database setup
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test_auth_login.db"
engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


# Mock Redis client for testing
class MockRedis:
    """Mock Redis client for testing."""
    def __init__(self):
        self.data = {}
        self.expiry = {}
    
    def hset(self, key, mapping=None, **kwargs):
        """Mock hset operation."""
        if mapping:
            self.data[key] = mapping
        else:
            if key not in self.data:
                self.data[key] = {}
            self.data[key].update(kwargs)
    
    def expire(self, key, seconds):
        """Mock expire operation."""
        self.expiry[key] = seconds
    
    def hgetall(self, key):
        """Mock hgetall operation."""
        return self.data.get(key, {})
    
    def delete(self, key):
        """Mock delete operation."""
        if key in self.data:
            del self.data[key]
        if key in self.expiry:
            del self.expiry[key]
    
    def exists(self, key):
        """Mock exists operation."""
        return 1 if key in self.data else 0


mock_redis = MockRedis()

# Override the redis_client in the database module
database.redis_client = mock_redis

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_database():
    """Create and drop test database for each test."""
    Base.metadata.create_all(bind=engine)
    # Clear mock Redis
    mock_redis.data = {}
    mock_redis.expiry = {}
    yield
    Base.metadata.drop_all(bind=engine)


def create_test_user(phone_number="+919876543210", user_type="rider", phone_verified=True):
    """Helper function to create a test user."""
    db = TestingSessionLocal()
    user = User(
        user_id=f"test-user-{phone_number}",
        phone_number=phone_number,
        phone_verified=phone_verified,
        name="Test User",
        email=f"test{phone_number}@example.com",
        user_type=UserType.RIDER if user_type == "rider" else UserType.DRIVER,
        password_hash=hash_password("testpassword123"),
        created_at=datetime.utcnow()
    )
    db.add(user)
    
    if user_type == "driver":
        driver_profile = DriverProfile(
            driver_id=user.user_id,
            license_number="DL1234567890",
            license_verified=False,
            vehicle_registration="MP09AB1234",
            vehicle_make="Toyota",
            vehicle_model="Innova",
            vehicle_color="White",
            vehicle_verified=False,
            insurance_expiry=datetime.utcnow() + timedelta(days=60),
            status=DriverStatus.UNAVAILABLE
        )
        db.add(driver_profile)
    
    db.commit()
    db.close()
    return user


class TestLoginSuccess:
    """Test successful login scenarios (Requirement 1.8)."""
    
    def test_login_rider_success(self):
        """Test successful login for a rider with valid credentials."""
        create_test_user(phone_number="+919876543210", user_type="rider")
        
        response = client.post("/api/auth/login", json={
            "phone_number": "+919876543210",
            "password": "testpassword123"
        })
        
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user_id"] == "test-user-+919876543210"
        assert data["phone_number"] == "+919876543210"
        assert data["name"] == "Test User"
        assert data["user_type"] == "rider"
        assert data["phone_verified"] is True
        assert "message" in data
    
    def test_login_driver_success(self):
        """Test successful login for a driver with valid credentials."""
        create_test_user(phone_number="+919876543211", user_type="driver")
        
        response = client.post("/api/auth/login", json={
            "phone_number": "+919876543211",
            "password": "testpassword123"
        })
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["user_type"] == "driver"
        assert "access_token" in data
    
    def test_login_unverified_phone_success(self):
        """Test that users can login even if phone is not verified."""
        create_test_user(phone_number="+919876543212", phone_verified=False)
        
        response = client.post("/api/auth/login", json={
            "phone_number": "+919876543212",
            "password": "testpassword123"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["phone_verified"] is False


class TestJWTTokenGeneration:
    """Test JWT token generation and claims (Requirement 1.8)."""
    
    def test_jwt_token_contains_user_claims(self):
        """Test that JWT token contains user_id, user_type, and phone_verified claims."""
        create_test_user(phone_number="+919876543210", user_type="rider")
        
        response = client.post("/api/auth/login", json={
            "phone_number": "+919876543210",
            "password": "testpassword123"
        })
        
        assert response.status_code == 200
        token = response.json()["access_token"]
        
        # Decode token
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        
        assert payload["user_id"] == "test-user-+919876543210"
        assert payload["user_type"] == "rider"
        assert payload["phone_verified"] is True
        assert "exp" in payload
        assert "iat" in payload
        assert "sub" in payload
    
    def test_jwt_token_expiration_set(self):
        """Test that JWT token has proper expiration time."""
        create_test_user(phone_number="+919876543210")
        
        response = client.post("/api/auth/login", json={
            "phone_number": "+919876543210",
            "password": "testpassword123"
        })
        
        token = response.json()["access_token"]
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        
        # Check expiration is set correctly
        exp_time = datetime.fromtimestamp(payload["exp"])
        iat_time = datetime.fromtimestamp(payload["iat"])
        
        time_diff = (exp_time - iat_time).total_seconds() / 60
        assert abs(time_diff - settings.jwt_access_token_expire_minutes) < 1  # Within 1 minute tolerance
    
    def test_jwt_token_driver_claims(self):
        """Test that driver JWT token contains correct user_type."""
        create_test_user(phone_number="+919876543211", user_type="driver")
        
        response = client.post("/api/auth/login", json={
            "phone_number": "+919876543211",
            "password": "testpassword123"
        })
        
        token = response.json()["access_token"]
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        
        assert payload["user_type"] == "driver"


class TestRedisSessionStorage:
    """Test Redis session storage (Requirement 1.8)."""
    
    def test_session_stored_in_redis(self):
        """Test that login creates a session in Redis."""
        create_test_user(phone_number="+919876543210")
        
        response = client.post("/api/auth/login", json={
            "phone_number": "+919876543210",
            "password": "testpassword123"
        })
        
        assert response.status_code == 200
        user_id = response.json()["user_id"]
        
        # Check Redis session
        session_key = f"session:{user_id}"
        session_data = mock_redis.hgetall(session_key)
        
        assert session_data is not None
        assert session_data["user_id"] == user_id
        assert session_data["phone_number"] == "+919876543210"
        assert session_data["user_type"] == "rider"
        assert session_data["phone_verified"] == "True"
        assert "login_time" in session_data
    
    def test_session_has_expiration(self):
        """Test that Redis session has expiration matching JWT token."""
        create_test_user(phone_number="+919876543210")
        
        response = client.post("/api/auth/login", json={
            "phone_number": "+919876543210",
            "password": "testpassword123"
        })
        
        user_id = response.json()["user_id"]
        session_key = f"session:{user_id}"
        
        # Check expiration is set
        assert session_key in mock_redis.expiry
        expected_expiry = settings.jwt_access_token_expire_minutes * 60
        assert mock_redis.expiry[session_key] == expected_expiry
    
    def test_session_contains_all_required_fields(self):
        """Test that session contains user_id, phone_number, user_type, phone_verified, and login_time."""
        create_test_user(phone_number="+919876543210", user_type="driver")
        
        response = client.post("/api/auth/login", json={
            "phone_number": "+919876543210",
            "password": "testpassword123"
        })
        
        user_id = response.json()["user_id"]
        session_key = f"session:{user_id}"
        session_data = mock_redis.hgetall(session_key)
        
        required_fields = ["user_id", "phone_number", "user_type", "phone_verified", "login_time"]
        for field in required_fields:
            assert field in session_data


class TestLoginFailure:
    """Test login failure scenarios."""
    
    def test_login_invalid_phone_number(self):
        """Test login with non-existent phone number."""
        response = client.post("/api/auth/login", json={
            "phone_number": "+919999999999",
            "password": "testpassword123"
        })
        
        assert response.status_code == 401
        assert "invalid phone number or password" in response.json()["detail"].lower()
    
    def test_login_incorrect_password(self):
        """Test login with incorrect password."""
        create_test_user(phone_number="+919876543210")
        
        response = client.post("/api/auth/login", json={
            "phone_number": "+919876543210",
            "password": "wrongpassword"
        })
        
        assert response.status_code == 401
        assert "invalid phone number or password" in response.json()["detail"].lower()
    
    def test_login_no_session_created_on_failure(self):
        """Test that no Redis session is created on failed login."""
        create_test_user(phone_number="+919876543210")
        
        response = client.post("/api/auth/login", json={
            "phone_number": "+919876543210",
            "password": "wrongpassword"
        })
        
        assert response.status_code == 401
        
        # Check no session in Redis
        user_id = "test-user-+919876543210"
        session_key = f"session:{user_id}"
        assert mock_redis.exists(session_key) == 0


class TestLoginValidation:
    """Test input validation for login."""
    
    def test_login_invalid_phone_format(self):
        """Test that invalid phone number format is rejected."""
        response = client.post("/api/auth/login", json={
            "phone_number": "1234567890",  # Missing +91
            "password": "testpassword123"
        })
        
        assert response.status_code == 422
    
    def test_login_password_too_short(self):
        """Test that short passwords are rejected."""
        response = client.post("/api/auth/login", json={
            "phone_number": "+919876543210",
            "password": "short"
        })
        
        assert response.status_code == 422
    
    def test_login_missing_phone_number(self):
        """Test that missing phone number is rejected."""
        response = client.post("/api/auth/login", json={
            "password": "testpassword123"
        })
        
        assert response.status_code == 422
    
    def test_login_missing_password(self):
        """Test that missing password is rejected."""
        response = client.post("/api/auth/login", json={
            "phone_number": "+919876543210"
        })
        
        assert response.status_code == 422


class TestPasswordVerification:
    """Test password verification during login."""
    
    def test_password_case_sensitive(self):
        """Test that password verification is case-sensitive."""
        create_test_user(phone_number="+919876543210")
        
        # Try with wrong case
        response = client.post("/api/auth/login", json={
            "phone_number": "+919876543210",
            "password": "TESTPASSWORD123"
        })
        
        assert response.status_code == 401
    
    def test_password_with_special_characters(self):
        """Test login with password containing special characters."""
        db = TestingSessionLocal()
        user = User(
            user_id="test-user-special",
            phone_number="+919876543213",
            phone_verified=True,
            name="Test User",
            email="test@example.com",
            user_type=UserType.RIDER,
            password_hash=hash_password("P@ssw0rd!#$%"),
            created_at=datetime.utcnow()
        )
        db.add(user)
        db.commit()
        db.close()
        
        response = client.post("/api/auth/login", json={
            "phone_number": "+919876543213",
            "password": "P@ssw0rd!#$%"
        })
        
        assert response.status_code == 200


class TestMultipleLogins:
    """Test multiple login scenarios."""
    
    def test_multiple_logins_same_user(self):
        """Test that same user can login multiple times (creates new session)."""
        create_test_user(phone_number="+919876543210")
        
        # First login
        response1 = client.post("/api/auth/login", json={
            "phone_number": "+919876543210",
            "password": "testpassword123"
        })
        token1 = response1.json()["access_token"]
        
        # Add small delay to ensure different iat timestamp
        import time
        time.sleep(1)
        
        # Second login
        response2 = client.post("/api/auth/login", json={
            "phone_number": "+919876543210",
            "password": "testpassword123"
        })
        token2 = response2.json()["access_token"]
        
        # Both should succeed
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        # Tokens should be different (different iat)
        assert token1 != token2
    
    def test_multiple_users_login(self):
        """Test that multiple users can login simultaneously."""
        create_test_user(phone_number="+919876543210", user_type="rider")
        create_test_user(phone_number="+919876543211", user_type="driver")
        
        response1 = client.post("/api/auth/login", json={
            "phone_number": "+919876543210",
            "password": "testpassword123"
        })
        
        response2 = client.post("/api/auth/login", json={
            "phone_number": "+919876543211",
            "password": "testpassword123"
        })
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        # Check both sessions exist
        user_id1 = response1.json()["user_id"]
        user_id2 = response2.json()["user_id"]
        
        assert mock_redis.exists(f"session:{user_id1}") == 1
        assert mock_redis.exists(f"session:{user_id2}") == 1
