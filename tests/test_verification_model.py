"""
Unit tests for VerificationSession model.
Tests basic functionality and business logic methods.
"""
import pytest
from datetime import datetime, timedelta
from app.models.verification import VerificationSession


def test_create_session():
    """Test creating a verification session with factory method."""
    phone = "+919876543210"
    code = "123456"
    session_id = "test-session-id"
    
    session = VerificationSession.create_session(phone, code, session_id)
    
    assert session.session_id == session_id
    assert session.phone_number == phone
    assert session.code == code
    assert session.attempts == 0
    assert session.verified is False
    assert session.blocked_until is None
    assert session.expires_at > datetime.utcnow()


def test_is_expired():
    """Test expiry checking."""
    session = VerificationSession(
        session_id="test-id",
        phone_number="+919876543210",
        code="123456",
        created_at=datetime.utcnow() - timedelta(minutes=15),
        expires_at=datetime.utcnow() - timedelta(minutes=5),
        attempts=0,
        verified=False
    )
    
    assert session.is_expired() is True


def test_is_not_expired():
    """Test that a fresh session is not expired."""
    session = VerificationSession.create_session("+919876543210", "123456", "test-id")
    assert session.is_expired() is False


def test_is_blocked():
    """Test blocking mechanism."""
    session = VerificationSession(
        session_id="test-id",
        phone_number="+919876543210",
        code="123456",
        created_at=datetime.utcnow(),
        expires_at=datetime.utcnow() + timedelta(minutes=10),
        attempts=3,
        verified=False,
        blocked_until=datetime.utcnow() + timedelta(minutes=30)
    )
    
    assert session.is_blocked() is True


def test_is_not_blocked():
    """Test that a session without blocking is not blocked."""
    session = VerificationSession.create_session("+919876543210", "123456", "test-id")
    assert session.is_blocked() is False


def test_can_attempt_verification_fresh_session():
    """Test that a fresh session allows verification attempts."""
    session = VerificationSession.create_session("+919876543210", "123456", "test-id")
    assert session.can_attempt_verification() is True


def test_cannot_attempt_when_verified():
    """Test that verified sessions don't allow more attempts."""
    session = VerificationSession.create_session("+919876543210", "123456", "test-id")
    session.verified = True
    assert session.can_attempt_verification() is False


def test_cannot_attempt_when_expired():
    """Test that expired sessions don't allow attempts."""
    session = VerificationSession(
        session_id="test-id",
        phone_number="+919876543210",
        code="123456",
        created_at=datetime.utcnow() - timedelta(minutes=15),
        expires_at=datetime.utcnow() - timedelta(minutes=5),
        attempts=0,
        verified=False
    )
    assert session.can_attempt_verification() is False


def test_cannot_attempt_when_blocked():
    """Test that blocked sessions don't allow attempts."""
    session = VerificationSession(
        session_id="test-id",
        phone_number="+919876543210",
        code="123456",
        created_at=datetime.utcnow(),
        expires_at=datetime.utcnow() + timedelta(minutes=10),
        attempts=3,
        verified=False,
        blocked_until=datetime.utcnow() + timedelta(minutes=30)
    )
    assert session.can_attempt_verification() is False


def test_cannot_attempt_after_3_attempts():
    """Test that sessions with 3 attempts don't allow more."""
    session = VerificationSession.create_session("+919876543210", "123456", "test-id")
    session.attempts = 3
    assert session.can_attempt_verification() is False


def test_increment_attempts():
    """Test incrementing attempt counter."""
    session = VerificationSession.create_session("+919876543210", "123456", "test-id")
    
    assert session.attempts == 0
    session.increment_attempts()
    assert session.attempts == 1
    assert session.blocked_until is None


def test_increment_attempts_blocks_after_third():
    """Test that third failed attempt blocks the session for 30 minutes."""
    session = VerificationSession.create_session("+919876543210", "123456", "test-id")
    
    # First two attempts don't block
    session.increment_attempts()
    session.increment_attempts()
    assert session.attempts == 2
    assert session.blocked_until is None
    
    # Third attempt blocks
    before_block = datetime.utcnow()
    session.increment_attempts()
    assert session.attempts == 3
    assert session.blocked_until is not None
    assert session.blocked_until > before_block
    # Should be blocked for approximately 30 minutes
    time_diff = (session.blocked_until - before_block).total_seconds()
    assert 1790 < time_diff < 1810  # Allow 10 second tolerance


def test_session_expiry_is_10_minutes():
    """Test that sessions expire after 10 minutes."""
    before_creation = datetime.utcnow()
    session = VerificationSession.create_session("+919876543210", "123456", "test-id")
    after_creation = datetime.utcnow()
    
    # Expiry should be 10 minutes from creation
    time_diff = (session.expires_at - session.created_at).total_seconds()
    assert 595 < time_diff < 605  # Allow 5 second tolerance
    
    # Verify it's in the future
    assert session.expires_at > after_creation
