"""
Rating Service for managing ratings and reviews.
Handles rating submission, average calculation, and driver flagging.
"""
from typing import List, Optional
from datetime import datetime
import uuid
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from app.models.rating import Rating
from app.models.ride import Ride, RideStatus
from app.models.user import User, DriverProfile


class RatingService:
    """Service for managing ratings and reviews."""
    
    def __init__(self, db: Session):
        """
        Initialize rating service.
        
        Args:
            db: Database session
        """
        self.db = db
    
    def submit_rating(
        self,
        ride_id: str,
        rater_id: str,
        ratee_id: str,
        stars: int,
        review: Optional[str] = None
    ) -> Rating:
        """
        Submit a rating for a completed ride.
        
        Args:
            ride_id: Ride identifier
            rater_id: User submitting the rating
            ratee_id: User being rated
            stars: Rating value (1-5)
            review: Optional review text (max 500 characters)
            
        Returns:
            Created rating record
            
        Raises:
            ValueError: If validation fails
        """
        # Validate stars range
        if stars < 1 or stars > 5:
            raise ValueError("Rating must be between 1 and 5 stars")
        
        # Validate review length
        if review and len(review) > 500:
            raise ValueError("Review text must not exceed 500 characters")
        
        # Verify ride exists and is completed
        ride = self.db.query(Ride).filter(Ride.ride_id == ride_id).first()
        if not ride:
            raise ValueError(f"Ride {ride_id} not found")
        
        if ride.status != RideStatus.COMPLETED:
            raise ValueError("Can only rate completed rides")
        
        # Verify payment is completed
        if ride.payment_status != "completed":
            raise ValueError("Can only rate rides with completed payment")
        
        # Verify rater is part of the ride
        if rater_id not in [ride.rider_id, ride.driver_id]:
            raise ValueError("Only ride participants can submit ratings")
        
        # Verify ratee is the other participant
        if ratee_id not in [ride.rider_id, ride.driver_id] or ratee_id == rater_id:
            raise ValueError("Invalid ratee for this ride")
        
        # Check if rating already exists
        existing_rating = self.db.query(Rating).filter(
            Rating.ride_id == ride_id,
            Rating.rater_id == rater_id,
            Rating.ratee_id == ratee_id
        ).first()
        
        if existing_rating:
            raise ValueError("Rating already submitted for this ride")
        
        # Create rating
        rating = Rating(
            rating_id=str(uuid.uuid4()),
            ride_id=ride_id,
            rater_id=rater_id,
            ratee_id=ratee_id,
            stars=stars,
            review=review
        )
        
        self.db.add(rating)
        self.db.commit()
        self.db.refresh(rating)
        
        # Update average rating for ratee
        self.calculate_and_update_average_rating(ratee_id)
        
        # Check if driver needs to be flagged
        ratee = self.db.query(User).filter(User.user_id == ratee_id).first()
        if ratee and ratee.user_type.value == "driver":
            self.check_and_flag_driver(ratee_id)
        
        return rating
    
    def calculate_and_update_average_rating(self, user_id: str) -> float:
        """
        Calculate average rating from last 100 rides and update user profile.
        
        Args:
            user_id: User identifier
            
        Returns:
            Calculated average rating
        """
        # Get last 100 ratings for this user
        ratings = self.db.query(Rating).filter(
            Rating.ratee_id == user_id
        ).order_by(desc(Rating.created_at)).limit(100).all()
        
        if not ratings:
            return 0.0
        
        # Calculate average
        total_stars = sum(r.stars for r in ratings)
        average_rating = total_stars / len(ratings)
        
        # Update user profile
        user = self.db.query(User).filter(User.user_id == user_id).first()
        if user:
            user.average_rating = round(average_rating, 2)
            user.total_rides = len(ratings)
            self.db.commit()
        
        return average_rating
    
    def check_and_flag_driver(self, driver_id: str) -> bool:
        """
        Check if driver's average rating is below 3.5 and flag account.
        
        Args:
            driver_id: Driver identifier
            
        Returns:
            True if driver was flagged, False otherwise
        """
        user = self.db.query(User).filter(User.user_id == driver_id).first()
        if not user or not user.driver_profile:
            return False
        
        # Check if average rating is below 3.5
        if user.average_rating < 3.5 and user.average_rating > 0:
            user.driver_profile.is_flagged = True
            self.db.commit()
            return True
        
        return False
    
    def get_user_ratings(
        self,
        user_id: str,
        as_rater: bool = False
    ) -> List[Rating]:
        """
        Get ratings for a user.
        
        Args:
            user_id: User identifier
            as_rater: If True, get ratings given by user; if False, get ratings received
            
        Returns:
            List of ratings
        """
        if as_rater:
            ratings = self.db.query(Rating).filter(
                Rating.rater_id == user_id
            ).order_by(desc(Rating.created_at)).all()
        else:
            ratings = self.db.query(Rating).filter(
                Rating.ratee_id == user_id
            ).order_by(desc(Rating.created_at)).all()
        
        return ratings
    
    def get_ride_ratings(self, ride_id: str) -> List[Rating]:
        """
        Get all ratings for a specific ride.
        
        Args:
            ride_id: Ride identifier
            
        Returns:
            List of ratings for the ride
        """
        ratings = self.db.query(Rating).filter(
            Rating.ride_id == ride_id
        ).all()
        
        return ratings
