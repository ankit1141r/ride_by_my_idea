"""
Unit tests for phone verification endpoints.
Tests Requirements 1.2, 1.3, 1.4
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import patch

from app.models.verification import VerificationSession
from app.models.user import User, UserType
from app.routers.auth import generate_otp


class TestOTPGeneration:
    """Test OTP code generation."""
    
    def test_generate_otp_returns_6_digits(self):
        """Test that OTP is exactly 6 digits."""
        otp = generate_otp()
        assert len(otp) == 6
        assert otp.isdigit()
    
    def test_generate_otp_returns_different_codes(self):
        """Test that OTP generation produces different codes."""
        otp1 = generate_otp()
        otp2 = generate_otp()
        # While theoretically they could be the same, probability is very low
        # Generate multiple to ensure randomness
        otps = [generate_otp() for _ in range(10)]
        assert len(set(otps)) > 1  # At least some variation


class TestSendVerificationCode:
    """Test sending verification codes (Requirement 1.2)."""
    
    @patch('app.routers.auth.send_sms')
    def test_send_verification_code_success(self, mock_send_sms, client):
        """Test successful verification code sending."""
        mock_send_sms.return_value = True
        
        response = client.post("/api/auth/verify/send", json={
            "phone_number": "+919876543210"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        assert data["phone_number"] == "+919876543210"
        assert "expires_at" in data
        assert "message" in data
        
        # Verify SMS was sent
        mock_send_sms.assert_called_once()
        call_args = mock_send_sms.call_args
        assert call_args[0][0] == "+919876543210"
        assert "verification code" in call_args[0][1].lower()
    
    @patch('app.routers.auth.send_sms')
    def test_send_verification_creates_session_in_database(self, mock_send_sms, client, db_session):
        """Test that verification session is created in database."""
        mock_send_sms.return_value = True
        
        response = client.post("/api/auth/verify/send", json={
            "phone_number": "+919876543210"
        })
        
        assert response.status_code == 200
        session_id = response.json()["session_id"]
        
        # Check database
        session = db_session.query(VerificationSession).filter(
            VerificationSession.session_id == session_id
        ).first()
        
        assert session is not None
        assert session.phone_number == "+919876543210"
        assert len(session.code) == 6
        assert session.code.isdigit()
        assert session.attempts == 0
        assert session.verified is False
        assert session.blocked_until is None
    
    @patch('app.routers.auth.send_sms')
    def test_send_verification_code_expires_in_10_minutes(self, mock_send_sms, client, db_session):
        """Test that verification code expires in 10 minutes (Requirement 1.3)."""
        mock_send_sms.return_value = True
        
        before_request = datetime.utcnow()
        response = client.post("/api/auth/verify/send", json={
            "phone_number": "+919876543210"
        })
        after_request = datetime.utcnow()
        
        assert response.status_code == 200
        session_id = response.json()["session_id"]
        
        # Check database
        session = db_session.query(VerificationSession).filter(
            VerificationSession.session_id == session_id
        ).first()
        
        # Verify expiry is 10 minutes from creation
        expected_expiry_min = before_request + timedelta(minutes=10)
        expected_expiry_max = after_request + timedelta(minutes=10)
        
        assert session.expires_at >= expected_expiry_min
        assert session.expires_at <= expected_expiry_max
    
    def test_send_verification_invalid_phone_format(self, client):
        """Test that invalid phone number format is rejected."""
        response = client.post("/api/auth/verify/send", json={
            "phone_number": "1234567890"  # Missing +91
        })
        
        assert response.status_code == 422
    
    @patch('app.routers.auth.send_sms')
    def test_send_verification_multiple_sessions_allowed(self, mock_send_sms, client):
        """Test that multiple verification sessions can be created."""
        mock_send_sms.return_value = True
        
        # First session
        response1 = client.post("/api/auth/verify/send", json={
            "phone_number": "+919876543210"
        })
        assert response1.status_code == 200
        
        # Second session (e.g., user didn't receive first SMS)
        response2 = client.post("/api/auth/verify/send", json={
            "phone_number": "+919876543210"
        })
        assert response2.status_code == 200
        
        # Should have different session IDs
        assert response1.json()["session_id"] != response2.json()["session_id"]


class TestConfirmVerificationCode:
    """Test confirming verification codes (Requirements 1.3, 1.4)."""
    
    @patch('app.routers.auth.send_sms')
    def test_confirm_verification_success(self, mock_send_sms, client, db_session):
        """Test successful verification confirmation."""
        mock_send_sms.return_value = True
        
        # Send verification code
        send_response = client.post("/api/auth/verify/send", json={
            "phone_number": "+919876543210"
        })
        session_id = send_response.json()["session_id"]
        
        # Get the code from database
        session = db_session.query(VerificationSession).filter(
            VerificationSession.session_id == session_id
        ).first()
        code = session.code
        
        # Confirm verification
        confirm_response = client.post("/api/auth/verify/confirm", json={
            "session_id": session_id,
            "code": code
        })
        
        assert confirm_response.status_code == 200
        data = confirm_response.json()
        assert data["verified"] is True
        assert data["phone_number"] == "+919876543210"
        assert "successfully" in data["message"].lower()
    
    @patch('app.routers.auth.send_sms')
    def test_confirm_verification_marks_session_verified(self, mock_send_sms, client, db_session):
        """Test that successful verification marks session as verified."""
        mock_send_sms.return_value = True
        
        # Send and confirm
        send_response = client.post("/api/auth/verify/send", json={
            "phone_number": "+919876543210"
        })
        session_id = send_response.json()["session_id"]
        
        session = db_session.query(VerificationSession).filter(
            VerificationSession.session_id == session_id
        ).first()
        code = session.code
        
        client.post("/api/auth/verify/confirm", json={
            "session_id": session_id,
            "code": code
        })
        
        # Check database - refresh the session
        db_session.expire_all()
        session = db_session.query(VerificationSession).filter(
            VerificationSession.session_id == session_id
        ).first()
        assert session.verified is True
    
    @patch('app.routers.auth.send_sms')
    def test_confirm_verification_updates_user_phone_verified(self, mock_send_sms, client, db_session):
        """Test that verification updates user's phone_verified status."""
        mock_send_sms.return_value = True
        
        # First register a user
        client.post("/api/auth/register", json={
            "phone_number": "+919876543210",
            "name": "John Doe",
            "email": "john@example.com",
            "password": "securepass123",
            "user_type": "rider"
        })
        
        # Send verification code
        send_response = client.post("/api/auth/verify/send", json={
            "phone_number": "+919876543210"
        })
        session_id = send_response.json()["session_id"]
        
        session = db_session.query(VerificationSession).filter(
            VerificationSession.session_id == session_id
        ).first()
        code = session.code
        
        # Confirm verification
        client.post("/api/auth/verify/confirm", json={
            "session_id": session_id,
            "code": code
        })
        
        # Check user's phone_verified status
        db_session.expire_all()
        user = db_session.query(User).filter(
            User.phone_number == "+919876543210"
        ).first()
        assert user.phone_verified is True
    
    @patch('app.routers.auth.send_sms')
    def test_confirm_verification_incorrect_code(self, mock_send_sms, client):
        """Test that incorrect code is rejected."""
        mock_send_sms.return_value = True
        
        send_response = client.post("/api/auth/verify/send", json={
            "phone_number": "+919876543210"
        })
        session_id = send_response.json()["session_id"]
        
        # Try with wrong code
        confirm_response = client.post("/api/auth/verify/confirm", json={
            "session_id": session_id,
            "code": "000000"  # Wrong code
        })
        
        assert confirm_response.status_code == 400
        assert "invalid" in confirm_response.json()["detail"].lower()
    
    def test_confirm_verification_invalid_session_id(self, client):
        """Test that invalid session ID is rejected."""
        response = client.post("/api/auth/verify/confirm", json={
            "session_id": "invalid-session-id",
            "code": "123456"
        })
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    @patch('app.routers.auth.send_sms')
    def test_confirm_verification_already_verified(self, mock_send_sms, client, db_session):
        """Test that already verified session returns success."""
        mock_send_sms.return_value = True
        
        # Send and verify
        send_response = client.post("/api/auth/verify/send", json={
            "phone_number": "+919876543210"
        })
        session_id = send_response.json()["session_id"]
        
        session = db_session.query(VerificationSession).filter(
            VerificationSession.session_id == session_id
        ).first()
        code = session.code
        
        # First verification
        client.post("/api/auth/verify/confirm", json={
            "session_id": session_id,
            "code": code
        })
        
        # Second verification attempt
        response = client.post("/api/auth/verify/confirm", json={
            "session_id": session_id,
            "code": code
        })
        
        assert response.status_code == 200
        assert "already verified" in response.json()["message"].lower()


class TestVerificationAttemptLimiting:
    """Test verification attempt limiting (Requirement 1.4)."""
    
    @patch('app.routers.auth.send_sms')
    def test_three_incorrect_attempts_allowed(self, mock_send_sms, client):
        """Test that 3 incorrect attempts are allowed before blocking."""
        mock_send_sms.return_value = True
        
        send_response = client.post("/api/auth/verify/send", json={
            "phone_number": "+919876543210"
        })
        session_id = send_response.json()["session_id"]
        
        # First attempt
        response1 = client.post("/api/auth/verify/confirm", json={
            "session_id": session_id,
            "code": "000000"
        })
        assert response1.status_code == 400
        assert "2 attempts remaining" in response1.json()["detail"]
        
        # Second attempt
        response2 = client.post("/api/auth/verify/confirm", json={
            "session_id": session_id,
            "code": "000000"
        })
        assert response2.status_code == 400
        assert "1 attempts remaining" in response2.json()["detail"]
        
        # Third attempt
        response3 = client.post("/api/auth/verify/confirm", json={
            "session_id": session_id,
            "code": "000000"
        })
        assert response3.status_code == 429
        assert "blocked" in response3.json()["detail"].lower()
    
    @patch('app.routers.auth.send_sms')
    def test_blocked_for_30_minutes_after_3_attempts(self, mock_send_sms, client, db_session):
        """Test that session is blocked for 30 minutes after 3 failed attempts (Requirement 1.4)."""
        mock_send_sms.return_value = True
        
        send_response = client.post("/api/auth/verify/send", json={
            "phone_number": "+919876543210"
        })
        session_id = send_response.json()["session_id"]
        
        # Make 3 failed attempts
        for _ in range(3):
            client.post("/api/auth/verify/confirm", json={
                "session_id": session_id,
                "code": "000000"
            })
        
        # Check database for blocked_until
        db_session.expire_all()
        session = db_session.query(VerificationSession).filter(
            VerificationSession.session_id == session_id
        ).first()
        
        assert session.blocked_until is not None
        assert session.attempts == 3
        
        # Verify blocked for approximately 30 minutes
        block_duration = session.blocked_until - datetime.utcnow()
        assert block_duration.total_seconds() >= 29 * 60  # At least 29 minutes
        assert block_duration.total_seconds() <= 31 * 60  # At most 31 minutes
    
    @patch('app.routers.auth.send_sms')
    def test_cannot_verify_while_blocked(self, mock_send_sms, client, db_session):
        """Test that verification is blocked during block period."""
        mock_send_sms.return_value = True
        
        send_response = client.post("/api/auth/verify/send", json={
            "phone_number": "+919876543210"
        })
        session_id = send_response.json()["session_id"]
        
        # Make 3 failed attempts to trigger block
        for _ in range(3):
            client.post("/api/auth/verify/confirm", json={
                "session_id": session_id,
                "code": "000000"
            })
        
        # Get correct code
        session = db_session.query(VerificationSession).filter(
            VerificationSession.session_id == session_id
        ).first()
        correct_code = session.code
        
        # Try with correct code while blocked
        response = client.post("/api/auth/verify/confirm", json={
            "session_id": session_id,
            "code": correct_code
        })
        
        assert response.status_code == 429
        detail = response.json()["detail"].lower()
        assert "too many" in detail or "blocked" in detail or "try again" in detail
    
    @patch('app.routers.auth.send_sms')
    def test_new_session_blocked_if_previous_blocked(self, mock_send_sms, client):
        """Test that new verification sessions are blocked if phone number is blocked."""
        mock_send_sms.return_value = True
        
        # First session - make 3 failed attempts
        send_response1 = client.post("/api/auth/verify/send", json={
            "phone_number": "+919876543210"
        })
        session_id1 = send_response1.json()["session_id"]
        
        for _ in range(3):
            client.post("/api/auth/verify/confirm", json={
                "session_id": session_id1,
                "code": "000000"
            })
        
        # Try to create new session for same phone number
        response = client.post("/api/auth/verify/send", json={
            "phone_number": "+919876543210"
        })
        
        assert response.status_code == 429
        assert "too many failed attempts" in response.json()["detail"].lower()


class TestVerificationExpiry:
    """Test verification code expiry (Requirement 1.3)."""
    
    @patch('app.routers.auth.send_sms')
    def test_expired_code_rejected(self, mock_send_sms, client, db_session):
        """Test that expired verification codes are rejected."""
        mock_send_sms.return_value = True
        
        send_response = client.post("/api/auth/verify/send", json={
            "phone_number": "+919876543210"
        })
        session_id = send_response.json()["session_id"]
        
        # Manually expire the session in database
        session = db_session.query(VerificationSession).filter(
            VerificationSession.session_id == session_id
        ).first()
        code = session.code
        session.expires_at = datetime.utcnow() - timedelta(minutes=1)  # Expired 1 minute ago
        db_session.commit()
        
        # Try to verify with expired code
        response = client.post("/api/auth/verify/confirm", json={
            "session_id": session_id,
            "code": code
        })
        
        assert response.status_code == 410
        assert "expired" in response.json()["detail"].lower()
    
    @patch('app.routers.auth.send_sms')
    def test_code_valid_within_10_minutes(self, mock_send_sms, client, db_session):
        """Test that code is valid within 10 minutes."""
        mock_send_sms.return_value = True
        
        send_response = client.post("/api/auth/verify/send", json={
            "phone_number": "+919876543210"
        })
        session_id = send_response.json()["session_id"]
        
        # Set expiry to 9 minutes from now (still valid)
        session = db_session.query(VerificationSession).filter(
            VerificationSession.session_id == session_id
        ).first()
        code = session.code
        session.expires_at = datetime.utcnow() + timedelta(minutes=9)
        db_session.commit()
        
        # Should still be valid
        response = client.post("/api/auth/verify/confirm", json={
            "session_id": session_id,
            "code": code
        })
        
        assert response.status_code == 200
        assert response.json()["verified"] is True


class TestVerificationCodeFormat:
    """Test verification code format validation."""
    
    @patch('app.routers.auth.send_sms')
    def test_code_must_be_6_digits(self, mock_send_sms, client):
        """Test that code must be exactly 6 digits."""
        mock_send_sms.return_value = True
        
        send_response = client.post("/api/auth/verify/send", json={
            "phone_number": "+919876543210"
        })
        session_id = send_response.json()["session_id"]
        
        # Try with 5 digits
        response = client.post("/api/auth/verify/confirm", json={
            "session_id": session_id,
            "code": "12345"
        })
        assert response.status_code == 422
        
        # Try with 7 digits
        response = client.post("/api/auth/verify/confirm", json={
            "session_id": session_id,
            "code": "1234567"
        })
        assert response.status_code == 422
    
    @patch('app.routers.auth.send_sms')
    def test_code_must_be_numeric(self, mock_send_sms, client):
        """Test that code must be numeric."""
        mock_send_sms.return_value = True
        
        send_response = client.post("/api/auth/verify/send", json={
            "phone_number": "+919876543210"
        })
        session_id = send_response.json()["session_id"]
        
        # Try with letters
        response = client.post("/api/auth/verify/confirm", json={
            "session_id": session_id,
            "code": "ABC123"
        })
        assert response.status_code == 422
