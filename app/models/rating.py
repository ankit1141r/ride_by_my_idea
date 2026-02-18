"""
Rating models for the ride-hailing platform.
Includes Rating model for ride ratings and reviews.
"""
from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Rating(Base):
    """Rating model for ride ratings and reviews."""
    __tablename__ = "ratings"
    
    rating_id = Column(String(36), primary_key=True)
    ride_id = Column(String(36), ForeignKey("rides.ride_id"), nullable=False, index=True)
    rater_id = Column(String(36), ForeignKey("users.user_id"), nullable=False, index=True)
    ratee_id = Column(String(36), ForeignKey("users.user_id"), nullable=False, index=True)
    
    # Rating details
    stars = Column(Integer, nullable=False)
    review = Column(String(500), nullable=True)
    
    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Constraints
    __table_args__ = (
        CheckConstraint('stars >= 1 AND stars <= 5', name='check_stars_range'),
    )
    
    def __repr__(self):
        return f"<Rating(rating_id={self.rating_id}, ride_id={self.ride_id}, stars={self.stars})>"
