"""
Verification models for the ride-hailing platform.
Includes VerificationSession model for phone verification.
"""
from sqlalchemy import Column, String, DateTime, Integer, Boolean
from datetime import datetime, timedelta
from app.database import Base


class VerificationSession(Base):
    """
    Verification session model for phone verification via SMS OTP.
    
    Tracks verification attempts and enforces security policies:
    - Codes expire after 10 minutes (Requirement 1.3)
    - Maximum 3 attempts allowed (Requirement 1.4)
    - Blocks further attempts for 30 minutes after 3 failed attempts (Requirement 1.4)
    """
    __tablename__ = "verification_sessions"
    
    session_id = Column(String(36), primary_key=True)
    phone_number = Column(String(15), nullable=False, index=True)
    code = Column(String(10), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False, index=True)
    
    # Attempt tracking
    attempts = Column(Integer, default=0, nullable=False)
    verified = Column(Boolean, default=False, nullable=False)
    
    # Blocking mechanism
    blocked_until = Column(DateTime, nullable=True, index=True)
    
    def __repr__(self):
        return f"<VerificationSession(session_id={self.session_id}, phone_number={self.phone_number}, verified={self.verified})>"
    
    def is_expired(self):
        """Check if the verification session has expired."""
        return datetime.utcnow() > self.expires_at
    
    def is_blocked(self):
        """Check if the session is currently blocked due to too many attempts."""
        if self.blocked_until is None:
            return False
        return datetime.utcnow() < self.blocked_until
    
    def can_attempt_verification(self):
        """Check if another verification attempt is allowed."""
        if self.verified:
            return False
        if self.is_expired():
            return False
        if self.is_blocked():
            return False
        if self.attempts >= 3:
            return False
        return True
    
    def increment_attempts(self):
        """
        Increment the attempt counter and block if limit reached.
        After 3 failed attempts, blocks for 30 minutes.
        """
        self.attempts += 1
        if self.attempts >= 3:
            self.blocked_until = datetime.utcnow() + timedelta(minutes=30)
    
    @staticmethod
    def create_session(phone_number: str, code: str, session_id: str):
        """
        Factory method to create a new verification session.
        Sets expiry to 10 minutes from creation.
        """
        now = datetime.utcnow()
        return VerificationSession(
            session_id=session_id,
            phone_number=phone_number,
            code=code,
            created_at=now,
            expires_at=now + timedelta(minutes=10),
            attempts=0,
            verified=False,
            blocked_until=None
        )
