"""
Rating endpoints for submitting and viewing ratings and reviews.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, Field

from app.database import get_db
from app.services.rating_service import RatingService
from app.utils.jwt import get_current_user
from app.models.rating import Rating


router = APIRouter(prefix="/api/ratings", tags=["ratings"])


# Request/Response schemas
class SubmitRatingRequest(BaseModel):
    """Request schema for submitting a rating."""
    ride_id: str
    ratee_id: str
    stars: int = Field(..., ge=1, le=5, description="Rating from 1 to 5 stars")
    review: Optional[str] = Field(None, max_length=500, description="Optional review text")


class RatingResponse(BaseModel):
    """Response schema for rating details."""
    rating_id: str
    ride_id: str
    rater_id: str
    ratee_id: str
    stars: int
    review: Optional[str]
    created_at: str
    
    class Config:
        from_attributes = True


class UserRatingsSummary(BaseModel):
    """Response schema for user ratings summary."""
    user_id: str
    average_rating: float
    total_rides: int
    is_flagged: bool = False


@router.post("", response_model=RatingResponse, status_code=status.HTTP_201_CREATED)
async def submit_rating(
    request: SubmitRatingRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Submit a rating for a completed ride.
    
    Args:
        request: Rating submission request
        current_user: Authenticated user
        db: Database session
        
    Returns:
        Created rating record
    """
    rating_service = RatingService(db)
    
    try:
        rating = rating_service.submit_rating(
            ride_id=request.ride_id,
            rater_id=current_user["user_id"],
            ratee_id=request.ratee_id,
            stars=request.stars,
            review=request.review
        )
        
        return RatingResponse(
            rating_id=rating.rating_id,
            ride_id=rating.ride_id,
            rater_id=rating.rater_id,
            ratee_id=rating.ratee_id,
            stars=rating.stars,
            review=rating.review,
            created_at=rating.created_at.isoformat()
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit rating: {str(e)}"
        )


@router.get("/received", response_model=List[RatingResponse])
async def get_received_ratings(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get ratings received by the current user.
    
    Args:
        current_user: Authenticated user
        db: Database session
        
    Returns:
        List of ratings received
    """
    rating_service = RatingService(db)
    ratings = rating_service.get_user_ratings(
        user_id=current_user["user_id"],
        as_rater=False
    )
    
    return [
        RatingResponse(
            rating_id=r.rating_id,
            ride_id=r.ride_id,
            rater_id=r.rater_id,
            ratee_id=r.ratee_id,
            stars=r.stars,
            review=r.review,
            created_at=r.created_at.isoformat()
        )
        for r in ratings
    ]


@router.get("/given", response_model=List[RatingResponse])
async def get_given_ratings(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get ratings given by the current user.
    
    Args:
        current_user: Authenticated user
        db: Database session
        
    Returns:
        List of ratings given
    """
    rating_service = RatingService(db)
    ratings = rating_service.get_user_ratings(
        user_id=current_user["user_id"],
        as_rater=True
    )
    
    return [
        RatingResponse(
            rating_id=r.rating_id,
            ride_id=r.ride_id,
            rater_id=r.rater_id,
            ratee_id=r.ratee_id,
            stars=r.stars,
            review=r.review,
            created_at=r.created_at.isoformat()
        )
        for r in ratings
    ]


@router.get("/ride/{ride_id}", response_model=List[RatingResponse])
async def get_ride_ratings(
    ride_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all ratings for a specific ride.
    
    Args:
        ride_id: Ride identifier
        current_user: Authenticated user
        db: Database session
        
    Returns:
        List of ratings for the ride
    """
    rating_service = RatingService(db)
    ratings = rating_service.get_ride_ratings(ride_id)
    
    return [
        RatingResponse(
            rating_id=r.rating_id,
            ride_id=r.ride_id,
            rater_id=r.rater_id,
            ratee_id=r.ratee_id,
            stars=r.stars,
            review=r.review,
            created_at=r.created_at.isoformat()
        )
        for r in ratings
    ]


@router.get("/summary/{user_id}", response_model=UserRatingsSummary)
async def get_user_rating_summary(
    user_id: str,
    db: Session = Depends(get_db)
):
    """
    Get rating summary for a user (public endpoint).
    
    Args:
        user_id: User identifier
        db: Database session
        
    Returns:
        User rating summary
    """
    from app.models.user import User
    
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    is_flagged = False
    if user.driver_profile:
        is_flagged = user.driver_profile.is_flagged
    
    return UserRatingsSummary(
        user_id=user.user_id,
        average_rating=user.average_rating,
        total_rides=user.total_rides,
        is_flagged=is_flagged
    )
