"""
Background job service for scheduled tasks.
Handles insurance expiry monitoring, payout processing, scheduled rides, and other scheduled jobs.
"""
from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.user import User, DriverProfile, DriverStatus
from app.models.ride import Ride, RideStatus
from app.services.location_service import LocationService
from app.database import get_mongodb


class BackgroundJobService:
    """Service for running background jobs."""
    
    def __init__(self, db: Session):
        """
        Initialize background job service.
        
        Args:
            db: Database session
        """
        self.db = db
    
    def check_insurance_expiry(self) -> List[str]:
        """
        Check for drivers with expired insurance and suspend them.
        Should be run daily.
        
        Returns:
            List of suspended driver IDs
        """
        now = datetime.utcnow()
        suspended_drivers = []
        
        # Find all drivers with expired insurance
        expired_drivers = self.db.query(User).join(DriverProfile).filter(
            User.user_type == "driver",
            DriverProfile.insurance_expiry <= now,
            DriverProfile.is_suspended == False
        ).all()
        
        for driver in expired_drivers:
            # Suspend driver
            driver.driver_profile.is_suspended = True
            driver.driver_profile.status = DriverStatus.UNAVAILABLE
            suspended_drivers.append(driver.user_id)
        
        if suspended_drivers:
            self.db.commit()
        
        return suspended_drivers
    
    def check_route_deviations(self) -> List[dict]:
        """
        Check for route deviations in active rides.
        Should be run every 30 seconds.
        
        Returns:
            List of deviation alerts
        """
        alerts = []
        
        # Get all in-progress rides
        active_rides = self.db.query(Ride).filter(
            Ride.status == RideStatus.IN_PROGRESS
        ).all()
        
        if not active_rides:
            return alerts
        
        # Get MongoDB connection
        mongodb = get_mongodb()
        location_service = LocationService(self.db, mongodb)
        
        for ride in active_rides:
            try:
                # Get driver's current location
                driver_location = location_service.get_driver_location(ride.driver_id)
                
                if not driver_location:
                    continue
                
                # Get expected route (simplified - in production would use actual route)
                # For now, we'll check if driver is significantly far from destination
                import json
                destination = json.loads(ride.destination)
                
                # Calculate distance from current location to destination
                distance = location_service.calculate_distance(
                    driver_location["latitude"],
                    driver_location["longitude"],
                    destination["latitude"],
                    destination["longitude"]
                )
                
                # Simple deviation check: if driver is moving away from destination
                # In production, this would use actual route polyline
                # For now, we'll just log significant deviations
                
                # This is a placeholder - actual implementation would need route polyline
                # and check distance from route, not just destination
                
            except Exception as e:
                # Log error but continue processing other rides
                print(f"Error checking route deviation for ride {ride.ride_id}: {str(e)}")
                continue
        
        return alerts
    
    def reset_daily_cancellation_counts(self) -> int:
        """
        Reset daily cancellation counts for all drivers.
        Should be run at midnight daily.
        
        Returns:
            Number of drivers reset
        """
        drivers = self.db.query(DriverProfile).filter(
            DriverProfile.cancellation_count > 0
        ).all()
        
        count = 0
        for driver in drivers:
            driver.cancellation_count = 0
            driver.last_cancellation_reset = datetime.utcnow()
            count += 1
        
        if count > 0:
            self.db.commit()
        
        return count
    
    def unsuspend_drivers_after_24_hours(self) -> List[str]:
        """
        Unsuspend drivers who were suspended for 24 hours due to cancellations.
        Should be run hourly.
        
        Returns:
            List of unsuspended driver IDs
        """
        from datetime import timedelta
        
        now = datetime.utcnow()
        cutoff_time = now - timedelta(hours=24)
        unsuspended_drivers = []
        
        # Find drivers suspended for cancellations more than 24 hours ago
        suspended_drivers = self.db.query(User).join(DriverProfile).filter(
            User.user_type == "driver",
            DriverProfile.is_suspended == True,
            DriverProfile.last_cancellation_reset <= cutoff_time,
            DriverProfile.cancellation_count >= 3
        ).all()
        
        for driver in suspended_drivers:
            # Unsuspend driver and reset cancellation count
            driver.driver_profile.is_suspended = False
            driver.driver_profile.cancellation_count = 0
            driver.driver_profile.last_cancellation_reset = now
            unsuspended_drivers.append(driver.user_id)
        
        if unsuspended_drivers:
            self.db.commit()
        
        return unsuspended_drivers
    
    def reset_daily_availability_hours(self) -> int:
        """
        Reset daily availability hours for all drivers.
        Should be run at midnight daily.
        
        Returns:
            Number of drivers reset
        """
        now = datetime.utcnow()
        count = 0
        
        # Get all driver profiles
        drivers = self.db.query(DriverProfile).all()
        
        for driver_profile in drivers:
            # If driver is currently available, calculate and accumulate current session hours
            if driver_profile.availability_start_time and driver_profile.status == DriverStatus.AVAILABLE:
                time_diff = now - driver_profile.availability_start_time
                hours_accumulated = time_diff.total_seconds() / 3600
                driver_profile.daily_availability_hours += hours_accumulated
                
                # Reset start time to now (beginning of new day)
                driver_profile.availability_start_time = now
            
            # Reset daily hours to 0
            driver_profile.daily_availability_hours = 0.0
            count += 1
        
        if count > 0:
            self.db.commit()
        
        return count
    
    def process_scheduled_rides(
        self,
        matching_service=None,
        notification_service=None
    ) -> dict:
        """
        Process scheduled rides (matching, reminders, no-driver handling).
        Should be run every minute.
        
        This is a wrapper that delegates to ScheduledRideService.
        
        Args:
            matching_service: Optional MatchingService instance
            notification_service: Optional NotificationService instance
        
        Returns:
            Dict with processing statistics
        
        Requirements: 16.5, 16.9, 16.10, 16.11
        """
        try:
            from app.services.scheduled_ride_service import ScheduledRideService
            
            # Create service instance
            scheduled_service = ScheduledRideService(
                self.db,
                matching_service,
                notification_service
            )
            
            # Process rides
            return scheduled_service.process_scheduled_rides()
        except Exception as e:
            print(f"Error processing scheduled rides: {str(e)}")
            return {
                "matching_triggered": 0,
                "rider_reminders_sent": 0,
                "driver_reminders_sent": 0,
                "no_driver_notifications": 0,
                "errors": [str(e)]
            }
