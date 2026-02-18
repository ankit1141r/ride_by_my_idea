"""
Unit tests for user registration endpoint.
Tests Requirements 1.1, 1.5, 1.7
"""
import pytest
from datetime import datetime, timedelta

from app.models.user import User, DriverProfile, UserType
from app.routers.auth import hash_password, verify_password


class TestPasswordHashing:
    """Test password hashing functionality (Requirement 1.7)."""
    
    def test_hash_password_returns_different_hash(self):
        """Test that hashing the same password twice produces different hashes."""
        password = "testpassword123"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        
        assert hash1 != hash2  # Different salts
        assert hash1 != password  # Not plain text
        assert hash2 != password
    
    def test_verify_password_correct(self):
        """Test that correct password verification works."""
        password = "testpassword123"
        hashed = hash_password(password)
        
        assert verify_password(password, hashed) is True
    
    def test_verify_password_incorrect(self):
        """Test that incorrect password verification fails."""
        password = "testpassword123"
        wrong_password = "wrongpassword"
        hashed = hash_password(password)
        
        assert verify_password(wrong_password, hashed) is False
    
    def test_password_not_stored_in_plain_text(self):
        """Test that passwords are hashed using bcrypt (Requirement 1.7)."""
        password = "testpassword123"
        hashed = hash_password(password)
        
        # Bcrypt hashes start with $2b$
        assert hashed.startswith('$2b$')
        assert password not in hashed


class TestRiderRegistration:
    """Test rider registration (Requirement 1.1)."""
    
    def test_register_rider_success(self, client):
        """Test successful rider registration with all required fields."""
        response = client.post("/api/auth/register", json={
            "phone_number": "+919876543210",
            "name": "John Doe",
            "email": "john@example.com",
            "password": "securepass123",
            "user_type": "rider"
        })
        
        assert response.status_code == 201
        data = response.json()
        assert data["phone_number"] == "+919876543210"
        assert data["name"] == "John Doe"
        assert data["email"] == "john@example.com"
        assert data["user_type"] == "rider"
        assert data["phone_verified"] is False
        assert "user_id" in data
        assert "created_at" in data
        assert "message" in data
    
    def test_register_rider_password_hashed_in_database(self, client, db_session):
        """Test that password is hashed in database (Requirement 1.7)."""
        plain_password = "securepass123"
        response = client.post("/api/auth/register", json={
            "phone_number": "+919876543210",
            "name": "John Doe",
            "email": "john@example.com",
            "password": plain_password,
            "user_type": "rider"
        })
        
        assert response.status_code == 201
        user_id = response.json()["user_id"]
        
        # Check database
        user = db_session.query(User).filter(User.user_id == user_id).first()
        
        assert user.password_hash != plain_password
        assert user.password_hash.startswith('$2b$')
        assert verify_password(plain_password, user.password_hash)
    
    def test_register_rider_without_vehicle_info(self, client):
        """Test that riders don't need vehicle information."""
        response = client.post("/api/auth/register", json={
            "phone_number": "+919876543210",
            "name": "John Doe",
            "email": "john@example.com",
            "password": "securepass123",
            "user_type": "rider"
        })
        
        assert response.status_code == 201
    
    def test_register_rider_with_vehicle_info_fails(self, client):
        """Test that riders cannot provide vehicle information."""
        response = client.post("/api/auth/register", json={
            "phone_number": "+919876543210",
            "name": "John Doe",
            "email": "john@example.com",
            "password": "securepass123",
            "user_type": "rider",
            "vehicle_info": {
                "registration_number": "MP09AB1234",
                "make": "Toyota",
                "model": "Innova",
                "color": "White",
                "license_number": "DL1234567890",
                "insurance_expiry": (datetime.utcnow() + timedelta(days=60)).isoformat()
            }
        })
        
        assert response.status_code == 422
        assert "vehicle information should not be provided for rider" in response.json()["detail"][0]["msg"].lower()


class TestDriverRegistration:
    """Test driver registration (Requirements 1.1, 1.5, 10.1)."""
    
    def test_register_driver_success_with_vehicle_info(self, client, db_session):
        """Test successful driver registration with vehicle information."""
        insurance_expiry = (datetime.utcnow() + timedelta(days=60)).isoformat()
        
        response = client.post("/api/auth/register", json={
            "phone_number": "+919876543210",
            "name": "Jane Driver",
            "email": "jane@example.com",
            "password": "securepass123",
            "user_type": "driver",
            "vehicle_info": {
                "registration_number": "MP09AB1234",
                "make": "Toyota",
                "model": "Innova",
                "color": "White",
                "license_number": "DL1234567890",
                "insurance_expiry": insurance_expiry
            }
        })
        
        assert response.status_code == 201
        data = response.json()
        assert data["user_type"] == "driver"
        assert data["phone_number"] == "+919876543210"
        
        # Verify driver profile created in database
        user = db_session.query(User).filter(User.user_id == data["user_id"]).first()
        assert user.driver_profile is not None
        assert user.driver_profile.vehicle_registration == "MP09AB1234"
        assert user.driver_profile.vehicle_make == "Toyota"
        assert user.driver_profile.vehicle_model == "Innova"
        assert user.driver_profile.vehicle_color == "White"
        assert user.driver_profile.license_number == "DL1234567890"
    
    def test_register_driver_without_vehicle_info_fails(self, client):
        """Test that driver registration fails without vehicle information (Requirement 1.5)."""
        response = client.post("/api/auth/register", json={
            "phone_number": "+919876543210",
            "name": "Jane Driver",
            "email": "jane@example.com",
            "password": "securepass123",
            "user_type": "driver"
        })
        
        assert response.status_code == 422
        assert "vehicle information is required for driver" in response.json()["detail"][0]["msg"].lower()
    
    def test_register_driver_all_vehicle_fields_required(self, client):
        """Test that all vehicle fields are required for drivers (Requirement 10.1)."""
        # Missing registration_number
        response = client.post("/api/auth/register", json={
            "phone_number": "+919876543210",
            "name": "Jane Driver",
            "email": "jane@example.com",
            "password": "securepass123",
            "user_type": "driver",
            "vehicle_info": {
                "make": "Toyota",
                "model": "Innova",
                "color": "White",
                "license_number": "DL1234567890",
                "insurance_expiry": (datetime.utcnow() + timedelta(days=60)).isoformat()
            }
        })
        
        assert response.status_code == 422
        assert "registration_number" in str(response.json())


class TestRegistrationValidation:
    """Test input validation for registration."""
    
    def test_invalid_phone_number_format(self, client):
        """Test that invalid phone number format is rejected."""
        response = client.post("/api/auth/register", json={
            "phone_number": "1234567890",  # Missing +91
            "name": "John Doe",
            "email": "john@example.com",
            "password": "securepass123",
            "user_type": "rider"
        })
        
        assert response.status_code == 422
    
    def test_invalid_email_format(self, client):
        """Test that invalid email format is rejected."""
        response = client.post("/api/auth/register", json={
            "phone_number": "+919876543210",
            "name": "John Doe",
            "email": "invalid-email",
            "password": "securepass123",
            "user_type": "rider"
        })
        
        assert response.status_code == 422
    
    def test_password_too_short(self, client):
        """Test that short passwords are rejected."""
        response = client.post("/api/auth/register", json={
            "phone_number": "+919876543210",
            "name": "John Doe",
            "email": "john@example.com",
            "password": "short",
            "user_type": "rider"
        })
        
        assert response.status_code == 422
    
    def test_invalid_user_type(self, client):
        """Test that invalid user types are rejected."""
        response = client.post("/api/auth/register", json={
            "phone_number": "+919876543210",
            "name": "John Doe",
            "email": "john@example.com",
            "password": "securepass123",
            "user_type": "admin"
        })
        
        assert response.status_code == 422
    
    def test_name_too_short(self, client):
        """Test that names shorter than 2 characters are rejected."""
        response = client.post("/api/auth/register", json={
            "phone_number": "+919876543210",
            "name": "J",
            "email": "john@example.com",
            "password": "securepass123",
            "user_type": "rider"
        })
        
        assert response.status_code == 422
    
    def test_missing_required_fields(self, client):
        """Test that missing required fields are rejected."""
        response = client.post("/api/auth/register", json={
            "phone_number": "+919876543210",
            "name": "John Doe"
            # Missing email, password, user_type
        })
        
        assert response.status_code == 422


class TestDuplicateRegistration:
    """Test duplicate user registration prevention."""
    
    def test_duplicate_phone_number(self, client):
        """Test that duplicate phone numbers are rejected."""
        # First registration
        client.post("/api/auth/register", json={
            "phone_number": "+919876543210",
            "name": "John Doe",
            "email": "john@example.com",
            "password": "securepass123",
            "user_type": "rider"
        })
        
        # Attempt duplicate registration
        response = client.post("/api/auth/register", json={
            "phone_number": "+919876543210",
            "name": "Jane Doe",
            "email": "jane@example.com",
            "password": "securepass123",
            "user_type": "rider"
        })
        
        assert response.status_code == 409
        assert "phone number already exists" in response.json()["detail"].lower()
    
    def test_duplicate_email(self, client):
        """Test that duplicate emails are rejected."""
        # First registration
        client.post("/api/auth/register", json={
            "phone_number": "+919876543210",
            "name": "John Doe",
            "email": "john@example.com",
            "password": "securepass123",
            "user_type": "rider"
        })
        
        # Attempt duplicate email
        response = client.post("/api/auth/register", json={
            "phone_number": "+919876543211",
            "name": "Jane Doe",
            "email": "john@example.com",
            "password": "securepass123",
            "user_type": "rider"
        })
        
        assert response.status_code == 409
        assert "email already exists" in response.json()["detail"].lower()


class TestInsuranceValidation:
    """Test insurance expiry validation (Requirement 10.3)."""
    
    def test_insurance_expiry_at_least_30_days(self, client):
        """Test that insurance must be valid for at least 30 days."""
        # Exactly 30 days - should pass
        insurance_expiry = (datetime.utcnow() + timedelta(days=30)).isoformat()
        
        response = client.post("/api/auth/register", json={
            "phone_number": "+919876543210",
            "name": "Jane Driver",
            "email": "jane@example.com",
            "password": "securepass123",
            "user_type": "driver",
            "vehicle_info": {
                "registration_number": "MP09AB1234",
                "make": "Toyota",
                "model": "Innova",
                "color": "White",
                "license_number": "DL1234567890",
                "insurance_expiry": insurance_expiry
            }
        })
        
        assert response.status_code == 201
    
    def test_insurance_expiry_less_than_30_days_fails(self, client):
        """Test that insurance expiring in less than 30 days is rejected."""
        # 29 days - should fail
        insurance_expiry = (datetime.utcnow() + timedelta(days=29)).isoformat()
        
        response = client.post("/api/auth/register", json={
            "phone_number": "+919876543210",
            "name": "Jane Driver",
            "email": "jane@example.com",
            "password": "securepass123",
            "user_type": "driver",
            "vehicle_info": {
                "registration_number": "MP09AB1234",
                "make": "Toyota",
                "model": "Innova",
                "color": "White",
                "license_number": "DL1234567890",
                "insurance_expiry": insurance_expiry
            }
        })
        
        assert response.status_code == 422
        assert "insurance must be valid for at least 30 days" in response.json()["detail"][0]["msg"].lower()
    
    def test_expired_insurance_fails(self, client):
        """Test that expired insurance is rejected."""
        # Past date
        insurance_expiry = (datetime.utcnow() - timedelta(days=1)).isoformat()
        
        response = client.post("/api/auth/register", json={
            "phone_number": "+919876543210",
            "name": "Jane Driver",
            "email": "jane@example.com",
            "password": "securepass123",
            "user_type": "driver",
            "vehicle_info": {
                "registration_number": "MP09AB1234",
                "make": "Toyota",
                "model": "Innova",
                "color": "White",
                "license_number": "DL1234567890",
                "insurance_expiry": insurance_expiry
            }
        })
        
        assert response.status_code == 422
