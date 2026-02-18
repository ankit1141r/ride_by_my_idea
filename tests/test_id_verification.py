"""
Tests for driver ID document verification endpoint.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import io
from pathlib import Path
import uuid

from app.main import app
from app.models.user import User, DriverProfile, UserType, DriverStatus
from app.database import get_db


@pytest.fixture
def driver_user(db_session: Session):
    """Create a test driver user with profile."""
    test_db = db_session
    user_id = str(uuid.uuid4())
    user = User(
        user_id=user_id,
        phone_number="+919876543210",
        phone_verified=True,
        name="Test Driver",
        email="driver@test.com",
        user_type=UserType.DRIVER,
        password_hash="hashed_password",
        created_at=datetime.utcnow()
    )
    
    driver_profile = DriverProfile(
        driver_id=user_id,
        license_number="DL1234567890",
        license_verified=False,
        vehicle_registration="MP09AB1234",
        vehicle_make="Toyota",
        vehicle_model="Innova",
        vehicle_color="White",
        vehicle_verified=False,
        insurance_expiry=datetime.utcnow() + timedelta(days=90),
        status=DriverStatus.UNAVAILABLE
    )
    
    test_db.add(user)
    test_db.add(driver_profile)
    test_db.commit()
    test_db.refresh(user)
    
    yield user
    
    # Cleanup
    test_db.query(DriverProfile).filter(DriverProfile.driver_id == user_id).delete()
    test_db.query(User).filter(User.user_id == user_id).delete()
    test_db.commit()


@pytest.fixture
def rider_user(db_session: Session):
    """Create a test rider user."""
    test_db = db_session
    user_id = str(uuid.uuid4())
    user = User(
        user_id=user_id,
        phone_number="+919876543211",
        phone_verified=True,
        name="Test Rider",
        email="rider@test.com",
        user_type=UserType.RIDER,
        password_hash="hashed_password",
        created_at=datetime.utcnow()
    )
    
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    
    yield user
    
    # Cleanup
    test_db.query(User).filter(User.user_id == user_id).delete()
    test_db.commit()


def create_test_image_file(filename: str = "test.jpg", size_mb: float = 1.0):
    """Create a test image file in memory."""
    # Create a file-like object with specified size
    size_bytes = int(size_mb * 1024 * 1024)
    content = b"fake_image_data" * (size_bytes // 15 + 1)
    content = content[:size_bytes]
    return io.BytesIO(content)


def cleanup_uploaded_files():
    """Clean up uploaded test files."""
    upload_dir = Path("uploads/id_documents")
    if upload_dir.exists():
        for file in upload_dir.glob("*"):
            if file.is_file():
                file.unlink()


class TestIDVerificationEndpoint:
    """Test suite for ID document verification endpoint."""
    
    def test_upload_valid_id_document(self, client, driver_user: User, db_session: Session):
        """Test successful ID document upload with valid data."""
        cleanup_uploaded_files()
        
        file_content = create_test_image_file("drivers_license.jpg", 1.0)
        
        response = client.post(
            "/api/auth/driver/verify-id",
            data={
                "user_id": driver_user.user_id,
                "document_type": "drivers_license"
            },
            files={
                "document": ("drivers_license.jpg", file_content, "image/jpeg")
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["driver_id"] == driver_user.user_id
        assert data["document_type"] == "drivers_license"
        assert data["verification_status"] == "pending"
        assert "document_path" in data
        assert "uploaded_at" in data
        
        # Verify database was updated
        driver_profile = db_session.query(DriverProfile).filter(
            DriverProfile.driver_id == driver_user.user_id
        ).first()
        
        assert driver_profile.id_document_type == "drivers_license"
        assert driver_profile.id_verification_status == "pending"
        assert driver_profile.id_document_path is not None
        assert driver_profile.id_document_uploaded_at is not None
        
        # Verify file was saved
        file_path = Path(driver_profile.id_document_path)
        assert file_path.exists()
        
        cleanup_uploaded_files()
    
    def test_upload_aadhaar_document(self, client, driver_user: User, db_session: Session):
        """Test uploading Aadhaar document."""
        cleanup_uploaded_files()
        
        file_content = create_test_image_file("aadhaar.png", 0.5)
        
        response = client.post(
            "/api/auth/driver/verify-id",
            data={
                "user_id": driver_user.user_id,
                "document_type": "aadhaar"
            },
            files={
                "document": ("aadhaar.png", file_content, "image/png")
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["document_type"] == "aadhaar"
        
        cleanup_uploaded_files()
    
    def test_upload_pan_document(self, client, driver_user: User, db_session: Session):
        """Test uploading PAN document."""
        cleanup_uploaded_files()
        
        file_content = create_test_image_file("pan.pdf", 0.3)
        
        response = client.post(
            "/api/auth/driver/verify-id",
            data={
                "user_id": driver_user.user_id,
                "document_type": "pan"
            },
            files={
                "document": ("pan.pdf", file_content, "application/pdf")
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["document_type"] == "pan"
        
        cleanup_uploaded_files()
    
    def test_reject_invalid_document_type(self, client, driver_user: User):
        """Test rejection of invalid document type."""
        file_content = create_test_image_file("invalid.jpg", 1.0)
        
        response = client.post(
            "/api/auth/driver/verify-id",
            data={
                "user_id": driver_user.user_id,
                "document_type": "passport"  # Invalid type
            },
            files={
                "document": ("invalid.jpg", file_content, "image/jpeg")
            }
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_reject_invalid_file_type(self, client, driver_user: User):
        """Test rejection of invalid file type."""
        file_content = io.BytesIO(b"not an image")
        
        response = client.post(
            "/api/auth/driver/verify-id",
            data={
                "user_id": driver_user.user_id,
                "document_type": "drivers_license"
            },
            files={
                "document": ("document.txt", file_content, "text/plain")
            }
        )
        
        assert response.status_code == 400
        assert "Invalid file type" in response.json()["detail"]
    
    def test_reject_file_too_large(self, client, driver_user: User):
        """Test rejection of file exceeding size limit."""
        # Create a file larger than 5MB
        file_content = create_test_image_file("large.jpg", 6.0)
        
        response = client.post(
            "/api/auth/driver/verify-id",
            data={
                "user_id": driver_user.user_id,
                "document_type": "drivers_license"
            },
            files={
                "document": ("large.jpg", file_content, "image/jpeg")
            }
        )
        
        assert response.status_code == 413
        assert "File too large" in response.json()["detail"]
    
    def test_reject_empty_file(self, client, driver_user: User):
        """Test rejection of empty file."""
        file_content = io.BytesIO(b"")
        
        response = client.post(
            "/api/auth/driver/verify-id",
            data={
                "user_id": driver_user.user_id,
                "document_type": "drivers_license"
            },
            files={
                "document": ("empty.jpg", file_content, "image/jpeg")
            }
        )
        
        assert response.status_code == 400
        assert "Empty file" in response.json()["detail"]
    
    def test_reject_non_existent_user(self, client):
        """Test rejection when user doesn't exist."""
        file_content = create_test_image_file("test.jpg", 1.0)
        fake_user_id = str(uuid.uuid4())
        
        response = client.post(
            "/api/auth/driver/verify-id",
            data={
                "user_id": fake_user_id,
                "document_type": "drivers_license"
            },
            files={
                "document": ("test.jpg", file_content, "image/jpeg")
            }
        )
        
        assert response.status_code == 404
        assert "User not found" in response.json()["detail"]
    
    def test_reject_rider_upload(self, client, rider_user: User):
        """Test rejection when rider tries to upload ID document."""
        file_content = create_test_image_file("test.jpg", 1.0)
        
        response = client.post(
            "/api/auth/driver/verify-id",
            data={
                "user_id": rider_user.user_id,
                "document_type": "drivers_license"
            },
            files={
                "document": ("test.jpg", file_content, "image/jpeg")
            }
        )
        
        assert response.status_code == 400
        assert "Only drivers can upload ID documents" in response.json()["detail"]
    
    def test_multiple_uploads_update_existing(self, client, driver_user: User, db_session: Session):
        """Test that multiple uploads update the existing document."""
        cleanup_uploaded_files()
        
        # First upload
        file_content1 = create_test_image_file("first.jpg", 1.0)
        response1 = client.post(
            "/api/auth/driver/verify-id",
            data={
                "user_id": driver_user.user_id,
                "document_type": "drivers_license"
            },
            files={
                "document": ("first.jpg", file_content1, "image/jpeg")
            }
        )
        assert response1.status_code == 200
        first_path = response1.json()["document_path"]
        
        # Second upload
        file_content2 = create_test_image_file("second.jpg", 1.0)
        response2 = client.post(
            "/api/auth/driver/verify-id",
            data={
                "user_id": driver_user.user_id,
                "document_type": "aadhaar"
            },
            files={
                "document": ("second.jpg", file_content2, "image/jpeg")
            }
        )
        assert response2.status_code == 200
        second_path = response2.json()["document_path"]
        
        # Verify database has latest upload
        driver_profile = db_session.query(DriverProfile).filter(
            DriverProfile.driver_id == driver_user.user_id
        ).first()
        
        assert driver_profile.id_document_type == "aadhaar"
        assert driver_profile.id_document_path == second_path
        assert driver_profile.id_document_path != first_path
        
        cleanup_uploaded_files()
    
    def test_file_saved_with_correct_naming(self, client, driver_user: User, db_session: Session):
        """Test that uploaded file is saved with correct naming convention."""
        cleanup_uploaded_files()
        
        file_content = create_test_image_file("test.jpg", 1.0)
        
        response = client.post(
            "/api/auth/driver/verify-id",
            data={
                "user_id": driver_user.user_id,
                "document_type": "drivers_license"
            },
            files={
                "document": ("test.jpg", file_content, "image/jpeg")
            }
        )
        
        assert response.status_code == 200
        file_path = response.json()["document_path"]
        
        # Verify filename contains user_id and document_type
        assert driver_user.user_id in file_path
        assert "drivers_license" in file_path
        
        # Verify file exists
        assert Path(file_path).exists()
        
        cleanup_uploaded_files()


class TestIDVerificationValidation:
    """Test validation logic for ID verification."""
    
    def test_allowed_file_types(self, client, driver_user: User):
        """Test all allowed file types are accepted."""
        cleanup_uploaded_files()
        
        allowed_types = [
            ("test.jpg", "image/jpeg"),
            ("test.png", "image/png"),
            ("test.pdf", "application/pdf")
        ]
        
        for filename, content_type in allowed_types:
            file_content = create_test_image_file(filename, 0.5)
            
            response = client.post(
                "/api/auth/driver/verify-id",
                data={
                    "user_id": driver_user.user_id,
                    "document_type": "drivers_license"
                },
                files={
                    "document": (filename, file_content, content_type)
                }
            )
            
            assert response.status_code == 200, f"Failed for {content_type}"
        
        cleanup_uploaded_files()
    
    def test_file_size_boundary(self, client, driver_user: User):
        """Test file size at boundary (just under 5MB)."""
        cleanup_uploaded_files()
        
        # Test file just under 5MB
        file_content = create_test_image_file("boundary.jpg", 4.99)
        
        response = client.post(
            "/api/auth/driver/verify-id",
            data={
                "user_id": driver_user.user_id,
                "document_type": "drivers_license"
            },
            files={
                "document": ("boundary.jpg", file_content, "image/jpeg")
            }
        )
        
        assert response.status_code == 200
        
        cleanup_uploaded_files()
