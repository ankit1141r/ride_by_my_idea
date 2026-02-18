"""
Scheduled Ride Background Service
Handles matching triggers, reminders, and no-driver-found notifications.
"""
from datetime import datetime, timedelta
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.models.scheduled_ride import ScheduledRide, ScheduledRideStatus
from app.services.matching_service import MatchingService
from app.services.notification_service import NotificationService


class ScheduledRideService:
    """Service for managing scheduled ride background tasks."""
    
    def __init__(self, db: Session, matching_service: MatchingService, notification_service: NotificationService):
        self.db = db
        self.matching_service = matching_service
        self.notification_service = notification_service
    
    def process_scheduled_rides(self) -> Dict[str, Any]:
        """
        Process all scheduled rides that need attention.
        
        This method should be called every minute by a background scheduler.
        It handles:
        1. Triggering matching 30 minutes before pickup
        2. Sending reminders 15 minutes before pickup
        3. Handling no-driver-found cases 15 minutes after scheduled time
        
        Requirements: 16.5, 16.9, 16.10, 16.11
        
        Returns:
            Dict with processing statistics
        """
        now = datetime.utcnow()
        
        stats = {
            "matching_triggered": 0,
            "rider_reminders_sent": 0,
            "driver_reminders_sent": 0,
            "no_driver_notifications": 0,
            "errors": []
        }
        
        # 1. Trigger matching for rides 30 minutes before pickup
        stats["matching_triggered"] = self._trigger_matching(now)
        
        # 2. Send reminders 15 minutes before pickup
        rider_reminders, driver_reminders = self._send_reminders(now)
        stats["rider_reminders_sent"] = rider_reminders
        stats["driver_reminders_sent"] = driver_reminders
        
        # 3. Handle no-driver-found cases
        stats["no_driver_notifications"] = self._handle_no_driver_found(now)
        
        return stats
    
    def _trigger_matching(self, now: datetime) -> int:
        """
        Trigger matching for scheduled rides 30 minutes before pickup.
        
        Requirements: 16.5
        """
        # Find rides that are scheduled and need matching
        # (scheduled_pickup_time - 30 minutes <= now AND status = scheduled)
        matching_window_start = now
        matching_window_end = now + timedelta(minutes=1)  # Process rides in next minute
        
        rides_to_match = self.db.query(ScheduledRide).filter(
            ScheduledRide.status == ScheduledRideStatus.SCHEDULED,
            ScheduledRide.scheduled_pickup_time >= matching_window_start + timedelta(minutes=29),
            ScheduledRide.scheduled_pickup_time <= matching_window_end + timedelta(minutes=30)
        ).all()
        
        count = 0
        for ride in rides_to_match:
            try:
                # Update status to matching
                ride.status = ScheduledRideStatus.MATCHING
                self.db.commit()
                
                # Trigger matching engine
                self.matching_service.broadcast_ride_request(
                    ride_id=ride.ride_id,
                    pickup_latitude=ride.pickup_location["latitude"],
                    pickup_longitude=ride.pickup_location["longitude"],
                    destination_latitude=ride.destination["latitude"],
                    destination_longitude=ride.destination["longitude"],
                    estimated_fare=ride.estimated_fare
                )
                
                count += 1
            except Exception as e:
                print(f"Error triggering matching for ride {ride.ride_id}: {str(e)}")
                continue
        
        return count
    
    def _send_reminders(self, now: datetime) -> tuple[int, int]:
        """
        Send reminders 15 minutes before pickup.
        
        Requirements: 16.9, 16.10
        
        Returns:
            Tuple of (rider_reminders_sent, driver_reminders_sent)
        """
        # Find rides that need reminders (15 minutes before pickup)
        reminder_window_start = now + timedelta(minutes=14)
        reminder_window_end = now + timedelta(minutes=16)
        
        # Rider reminders (for all rides in scheduled or matching status)
        rides_for_rider_reminder = self.db.query(ScheduledRide).filter(
            ScheduledRide.reminder_sent == False,
            ScheduledRide.status.in_([ScheduledRideStatus.SCHEDULED, ScheduledRideStatus.MATCHING, ScheduledRideStatus.MATCHED]),
            ScheduledRide.scheduled_pickup_time >= reminder_window_start,
            ScheduledRide.scheduled_pickup_time <= reminder_window_end
        ).all()
        
        rider_count = 0
        for ride in rides_for_rider_reminder:
            try:
                # Send reminder to rider
                self.notification_service.send_dual_notification(
                    user_id=ride.rider_id,
                    message=f"Reminder: Your scheduled ride is in 15 minutes. Pickup at {ride.pickup_location.get('address', 'your location')}.",
                    notification_type="scheduled_ride_reminder"
                )
                
                ride.reminder_sent = True
                self.db.commit()
                rider_count += 1
            except Exception as e:
                print(f"Error sending rider reminder for ride {ride.ride_id}: {str(e)}")
                continue
        
        # Driver reminders (only for matched rides)
        rides_for_driver_reminder = self.db.query(ScheduledRide).filter(
            ScheduledRide.driver_reminder_sent == False,
            ScheduledRide.status == ScheduledRideStatus.MATCHED,
            ScheduledRide.driver_id.isnot(None),
            ScheduledRide.scheduled_pickup_time >= reminder_window_start,
            ScheduledRide.scheduled_pickup_time <= reminder_window_end
        ).all()
        
        driver_count = 0
        for ride in rides_for_driver_reminder:
            try:
                # Send reminder to driver
                self.notification_service.send_dual_notification(
                    user_id=ride.driver_id,
                    message=f"Reminder: Scheduled pickup in 15 minutes at {ride.pickup_location.get('address', 'pickup location')}.",
                    notification_type="scheduled_ride_driver_reminder"
                )
                
                ride.driver_reminder_sent = True
                self.db.commit()
                driver_count += 1
            except Exception as e:
                print(f"Error sending driver reminder for ride {ride.ride_id}: {str(e)}")
                continue
        
        return rider_count, driver_count
    
    def _handle_no_driver_found(self, now: datetime) -> int:
        """
        Handle rides that are still in matching status 15 minutes past scheduled time.
        
        Requirements: 16.11
        """
        # Find rides that are 15+ minutes past scheduled time and still matching
        cutoff_time = now - timedelta(minutes=15)
        
        rides_no_driver = self.db.query(ScheduledRide).filter(
            ScheduledRide.status == ScheduledRideStatus.MATCHING,
            ScheduledRide.scheduled_pickup_time <= cutoff_time
        ).all()
        
        count = 0
        for ride in rides_no_driver:
            try:
                # Update status
                ride.status = ScheduledRideStatus.NO_DRIVER_FOUND
                self.db.commit()
                
                # Send notification to rider
                self.notification_service.send_dual_notification(
                    user_id=ride.rider_id,
                    message=f"We couldn't find a driver for your scheduled ride. You can reschedule or cancel for a full refund.",
                    notification_type="scheduled_ride_no_driver"
                )
                
                count += 1
            except Exception as e:
                print(f"Error handling no-driver for ride {ride.ride_id}: {str(e)}")
                continue
        
        return count


def get_scheduled_ride_service(
    db: Session,
    matching_service: MatchingService,
    notification_service: NotificationService
) -> ScheduledRideService:
    """Dependency injection for ScheduledRideService."""
    return ScheduledRideService(db, matching_service, notification_service)
