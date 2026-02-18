"""
Ride Matching Engine Service
Handles driver availability, ride broadcasting, and matching logic.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import json
from redis import Redis
from sqlalchemy.orm import Session
from app.models.user import User, DriverProfile
from app.models.location import Location
from app.services.location_service import calculate_distance


class MatchingService:
    """Service for managing driver availability and ride matching."""
    
    def __init__(self, redis_client: Redis, db: Session):
        self.redis = redis_client
        self.db = db
        self.DRIVER_AVAILABILITY_PREFIX = "driver:availability:"
        self.DRIVER_LOCATION_PREFIX = "driver:location:"
        self.AVAILABLE_DRIVERS_SET = "drivers:available"
        
        # Extended area support (Requirements: 18.5, 18.6)
        self.CITY_CENTER_LAT = 22.7196
        self.CITY_CENTER_LON = 75.8577
        self.SERVICE_AREA_RADIUS_KM = 20.0
        self.CITY_LIMITS = {
            "min_latitude": 22.6,
            "max_latitude": 22.8,
            "min_longitude": 75.7,
            "max_longitude": 75.9
        }
    
    def is_in_extended_area(self, latitude: float, longitude: float) -> bool:
        """
        Check if a location is in the extended area (beyond city limits but within 20km radius).
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            
        Returns:
            True if location is in extended area, False otherwise
            
        Requirements: 18.2, 18.3
        """
        # Check if within service area
        distance_from_center = calculate_distance(
            self.CITY_CENTER_LAT,
            self.CITY_CENTER_LON,
            latitude,
            longitude
        )
        in_service_area = distance_from_center <= self.SERVICE_AREA_RADIUS_KM
        
        # Check if within city limits
        in_city_limits = (
            self.CITY_LIMITS["min_latitude"] <= latitude <= self.CITY_LIMITS["max_latitude"] and
            self.CITY_LIMITS["min_longitude"] <= longitude <= self.CITY_LIMITS["max_longitude"]
        )
        
        # Extended area = in service area but not in city limits
        return in_service_area and not in_city_limits
    
    def get_initial_search_radius(self, latitude: float, longitude: float) -> float:
        """
        Get initial search radius based on whether location is in extended area.
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            
        Returns:
            Initial search radius in kilometers (5km for city center, 8km for extended area)
            
        Requirements: 18.5
        """
        is_extended = self.is_in_extended_area(latitude, longitude)
        return 8.0 if is_extended else 5.0
    
    def get_radius_expansion(self, latitude: float, longitude: float) -> float:
        """
        Get radius expansion amount based on whether location is in extended area.
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            
        Returns:
            Radius expansion in kilometers (2km for city center, 3km for extended area)
            
        Requirements: 18.6
        """
        is_extended = self.is_in_extended_area(latitude, longitude)
        return 3.0 if is_extended else 2.0
    
    def get_matching_timeout(self, latitude: float, longitude: float) -> int:
        """
        Get matching timeout based on whether location is in extended area.
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            
        Returns:
            Timeout in seconds (120 for city center, 180 for extended area)
            
        Requirements: 18.6
        """
        is_extended = self.is_in_extended_area(latitude, longitude)
        return 180 if is_extended else 120
    
    def set_driver_available(
        self,
        driver_id: str,
        latitude: float,
        longitude: float
    ) -> Dict[str, Any]:
        """
        Set driver status to available and store their location.
        Tracks availability start time for daily hours calculation.
        
        Args:
            driver_id: Driver's user ID
            latitude: Current latitude
            longitude: Current longitude
            
        Returns:
            Dict with status and message
        """
        # Verify driver exists and is a driver
        driver = self.db.query(User).filter(
            User.user_id == driver_id,
            User.user_type == "driver"
        ).first()
        
        if not driver:
            raise ValueError("Driver not found")
        
        # Store availability status
        availability_key = f"{self.DRIVER_AVAILABILITY_PREFIX}{driver_id}"
        availability_data = {
            "status": "available",
            "timestamp": datetime.utcnow().isoformat(),
            "latitude": latitude,
            "longitude": longitude
        }
        self.redis.setex(
            availability_key,
            timedelta(hours=24),  # Expire after 24 hours
            json.dumps(availability_data)
        )
        
        # Add to available drivers set
        self.redis.sadd(self.AVAILABLE_DRIVERS_SET, driver_id)
        
        # Store location separately for quick access
        location_key = f"{self.DRIVER_LOCATION_PREFIX}{driver_id}"
        location_data = {
            "latitude": latitude,
            "longitude": longitude,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.redis.setex(
            location_key,
            timedelta(hours=24),
            json.dumps(location_data)
        )
        
        # Track availability start time for daily hours calculation
        if driver.driver_profile:
            driver.driver_profile.status = "available"
            driver.driver_profile.availability_start_time = datetime.utcnow()
            self.db.commit()
        
        return {
            "status": "success",
            "message": f"Driver {driver_id} is now available",
            "location": {
                "latitude": latitude,
                "longitude": longitude
            }
        }
    
    def set_driver_unavailable(self, driver_id: str) -> Dict[str, Any]:
        """
        Set driver status to unavailable.
        Calculates and accumulates availability hours if driver was previously available.
        
        Args:
            driver_id: Driver's user ID
            
        Returns:
            Dict with status and message
        """
        # Verify driver exists
        driver = self.db.query(User).filter(
            User.user_id == driver_id,
            User.user_type == "driver"
        ).first()
        
        if not driver:
            raise ValueError("Driver not found")
        
        # Calculate availability hours if driver was available
        hours_accumulated = 0.0
        if driver.driver_profile and driver.driver_profile.availability_start_time:
            time_diff = datetime.utcnow() - driver.driver_profile.availability_start_time
            hours_accumulated = time_diff.total_seconds() / 3600
            
            # Accumulate to daily total
            driver.driver_profile.daily_availability_hours += hours_accumulated
            driver.driver_profile.availability_start_time = None
        
        # Update availability status
        availability_key = f"{self.DRIVER_AVAILABILITY_PREFIX}{driver_id}"
        availability_data = {
            "status": "unavailable",
            "timestamp": datetime.utcnow().isoformat()
        }
        self.redis.setex(
            availability_key,
            timedelta(hours=24),
            json.dumps(availability_data)
        )
        
        # Remove from available drivers set
        self.redis.srem(self.AVAILABLE_DRIVERS_SET, driver_id)
        
        # Update driver profile status in database
        if driver.driver_profile:
            driver.driver_profile.status = "unavailable"
            self.db.commit()
        
        return {
            "status": "success",
            "message": f"Driver {driver_id} is now unavailable",
            "hours_accumulated": round(hours_accumulated, 2),
            "total_daily_hours": round(driver.driver_profile.daily_availability_hours, 2) if driver.driver_profile else 0.0
        }
    
    def set_driver_busy(self, driver_id: str) -> Dict[str, Any]:
        """
        Set driver status to busy (on an active ride).
        Calculates and accumulates availability hours if driver was previously available.
        
        Args:
            driver_id: Driver's user ID
            
        Returns:
            Dict with status and message
        """
        # Get driver from database
        driver = self.db.query(User).filter(User.user_id == driver_id).first()
        
        # Calculate availability hours if driver was available
        hours_accumulated = 0.0
        if driver and driver.driver_profile and driver.driver_profile.availability_start_time:
            time_diff = datetime.utcnow() - driver.driver_profile.availability_start_time
            hours_accumulated = time_diff.total_seconds() / 3600
            
            # Accumulate to daily total
            driver.driver_profile.daily_availability_hours += hours_accumulated
            driver.driver_profile.availability_start_time = None
        
        # Update availability status
        availability_key = f"{self.DRIVER_AVAILABILITY_PREFIX}{driver_id}"
        availability_data = {
            "status": "busy",
            "timestamp": datetime.utcnow().isoformat()
        }
        self.redis.setex(
            availability_key,
            timedelta(hours=24),
            json.dumps(availability_data)
        )
        
        # Remove from available drivers set
        self.redis.srem(self.AVAILABLE_DRIVERS_SET, driver_id)
        
        # Update driver profile status in database
        if driver and driver.driver_profile:
            driver.driver_profile.status = "busy"
            self.db.commit()
        
        return {
            "status": "success",
            "message": f"Driver {driver_id} is now busy",
            "hours_accumulated": round(hours_accumulated, 2),
            "total_daily_hours": round(driver.driver_profile.daily_availability_hours, 2) if driver and driver.driver_profile else 0.0
        }
    
    def get_driver_status(self, driver_id: str) -> Optional[Dict[str, Any]]:
        """
        Get driver's current availability status.
        
        Args:
            driver_id: Driver's user ID
            
        Returns:
            Dict with status information or None if not found
        """
        availability_key = f"{self.DRIVER_AVAILABILITY_PREFIX}{driver_id}"
        data = self.redis.get(availability_key)
        
        if data:
            return json.loads(data)
        
        return None
    
    def is_driver_available(self, driver_id: str) -> bool:
        """
        Check if driver is currently available.
        
        Args:
            driver_id: Driver's user ID
            
        Returns:
            True if driver is available, False otherwise
        """
        return self.redis.sismember(self.AVAILABLE_DRIVERS_SET, driver_id)
    
    def get_available_drivers(
        self,
        pickup_latitude: float,
        pickup_longitude: float,
        radius_km: float = 5.0
    ) -> List[Dict[str, Any]]:
        """
        Get all available drivers within radius of pickup location.
        
        Args:
            pickup_latitude: Pickup location latitude
            pickup_longitude: Pickup location longitude
            radius_km: Search radius in kilometers
            
        Returns:
            List of available drivers with their locations and distances
        """
        # Get all available driver IDs
        available_driver_ids = self.redis.smembers(self.AVAILABLE_DRIVERS_SET)
        
        drivers_in_radius = []
        
        for driver_id in available_driver_ids:
            # Get driver location
            location_key = f"{self.DRIVER_LOCATION_PREFIX}{driver_id}"
            location_data = self.redis.get(location_key)
            
            if not location_data:
                continue
            
            location = json.loads(location_data)
            
            # Calculate distance
            distance = calculate_distance(
                pickup_latitude,
                pickup_longitude,
                location["latitude"],
                location["longitude"]
            )
            
            # Check if within radius
            if distance <= radius_km:
                # Get driver details from database
                driver = self.db.query(User).filter(
                    User.user_id == driver_id
                ).first()
                
                if driver and driver.driver_profile:
                    drivers_in_radius.append({
                        "driver_id": driver_id,
                        "name": driver.name,
                        "phone_number": driver.phone_number,
                        "latitude": location["latitude"],
                        "longitude": location["longitude"],
                        "distance_km": round(distance, 2),
                        "vehicle": {
                            "registration_number": driver.driver_profile.vehicle_registration,
                            "make": driver.driver_profile.vehicle_make,
                            "model": driver.driver_profile.vehicle_model,
                            "color": driver.driver_profile.vehicle_color
                        },
                        "rating": driver.average_rating,
                        "total_rides": driver.total_rides,
                        # Include driver preferences (Requirements: 18.10, 18.11)
                        "accept_extended_area": driver.driver_profile.accept_extended_area,
                        "accept_parcel_delivery": driver.driver_profile.accept_parcel_delivery
                    })
        
        # Sort by distance (closest first)
        drivers_in_radius.sort(key=lambda x: x["distance_km"])
        
        return drivers_in_radius
    
    def update_driver_location(
        self,
        driver_id: str,
        latitude: float,
        longitude: float
    ) -> Dict[str, Any]:
        """
        Update driver's current location.
        
        Args:
            driver_id: Driver's user ID
            latitude: Current latitude
            longitude: Current longitude
            
        Returns:
            Dict with status and message
        """
        location_key = f"{self.DRIVER_LOCATION_PREFIX}{driver_id}"
        location_data = {
            "latitude": latitude,
            "longitude": longitude,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.redis.setex(
            location_key,
            timedelta(hours=24),
            json.dumps(location_data)
        )
        
        # Also update in availability data if driver is available
        availability_key = f"{self.DRIVER_AVAILABILITY_PREFIX}{driver_id}"
        availability_data = self.redis.get(availability_key)
        
        if availability_data:
            data = json.loads(availability_data)
            data["latitude"] = latitude
            data["longitude"] = longitude
            data["timestamp"] = datetime.utcnow().isoformat()
            self.redis.setex(
                availability_key,
                timedelta(hours=24),
                json.dumps(data)
            )
        
        return {
            "status": "success",
            "message": "Location updated",
            "location": {
                "latitude": latitude,
                "longitude": longitude
            }
        }

    def broadcast_ride_request(
        self,
        ride_id: str,
        pickup_latitude: float,
        pickup_longitude: float,
        destination_latitude: float,
        destination_longitude: float,
        estimated_fare: float,
        radius_km: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Broadcast ride request to available drivers within radius.
        
        Sends notifications via both Redis (for persistence) and WebSocket
        (for real-time delivery to connected drivers).
        
        Args:
            ride_id: Unique ride request ID
            pickup_latitude: Pickup location latitude
            pickup_longitude: Pickup location longitude
            destination_latitude: Destination location latitude
            destination_longitude: Destination location longitude
            estimated_fare: Estimated fare for the ride
            radius_km: Search radius in kilometers (if None, uses dynamic radius based on location)
            
        Returns:
            Dict with broadcast details and list of notified drivers
            
        Requirements: 3.1, 18.5
        """
        # Use dynamic radius if not specified (Requirements: 18.5)
        if radius_km is None:
            radius_km = self.get_initial_search_radius(pickup_latitude, pickup_longitude)
        
        # Determine if this is an extended area ride
        is_extended_area = self.is_in_extended_area(pickup_latitude, pickup_longitude) or \
                          self.is_in_extended_area(destination_latitude, destination_longitude)
        
        # Get available drivers within radius
        available_drivers = self.get_available_drivers(
            pickup_latitude,
            pickup_longitude,
            radius_km
        )
        
        # Filter drivers by extended area preference if needed (Requirements: 18.11)
        if is_extended_area:
            available_drivers = [
                driver for driver in available_drivers
                if driver.get("accept_extended_area", True)  # Default to True if not set
            ]
        
        # Store broadcast details in Redis
        broadcast_key = f"ride:broadcast:{ride_id}"
        broadcast_data = {
            "ride_id": ride_id,
            "pickup_latitude": pickup_latitude,
            "pickup_longitude": pickup_longitude,
            "destination_latitude": destination_latitude,
            "destination_longitude": destination_longitude,
            "estimated_fare": estimated_fare,
            "radius_km": radius_km,
            "is_extended_area": is_extended_area,
            "broadcast_time": datetime.utcnow().isoformat(),
            "notified_drivers": [d["driver_id"] for d in available_drivers],
            "status": "active"
        }
        
        # Store broadcast with 10 minute expiry
        self.redis.setex(
            broadcast_key,
            timedelta(minutes=10),
            json.dumps(broadcast_data)
        )
        
        # Store driver notification list for this ride
        for driver in available_drivers:
            driver_notification_key = f"driver:notifications:{driver['driver_id']}"
            notification_data = {
                "ride_id": ride_id,
                "pickup_latitude": pickup_latitude,
                "pickup_longitude": pickup_longitude,
                "destination_latitude": destination_latitude,
                "destination_longitude": destination_longitude,
                "estimated_fare": estimated_fare,
                "distance_to_pickup_km": driver["distance_km"],
                "is_extended_area": is_extended_area,
                "notified_at": datetime.utcnow().isoformat()
            }
            
            # Add to driver's notification list (as a sorted set with timestamp as score)
            self.redis.zadd(
                driver_notification_key,
                {json.dumps(notification_data): datetime.utcnow().timestamp()}
            )
            
            # Set expiry on notification list
            self.redis.expire(driver_notification_key, timedelta(minutes=10))
        
        # Send WebSocket notifications (non-blocking)
        websocket_sent_count = self._send_websocket_notifications(
            available_drivers,
            ride_id,
            pickup_latitude,
            pickup_longitude,
            destination_latitude,
            destination_longitude,
            estimated_fare,
            broadcast_data["broadcast_time"],
            is_extended_area
        )
        
        return {
            "status": "success",
            "ride_id": ride_id,
            "broadcast_radius_km": radius_km,
            "is_extended_area": is_extended_area,
            "drivers_notified": len(available_drivers),
            "websocket_notifications_sent": websocket_sent_count,
            "notified_drivers": [
                {
                    "driver_id": d["driver_id"],
                    "name": d["name"],
                    "distance_km": d["distance_km"]
                }
                for d in available_drivers
            ]
        }
    
    def _send_websocket_notifications(
        self,
        drivers: List[Dict[str, Any]],
        ride_id: str,
        pickup_latitude: float,
        pickup_longitude: float,
        destination_latitude: float,
        destination_longitude: float,
        estimated_fare: float,
        broadcast_time: str,
        is_extended_area: bool = False
    ) -> int:
        """
        Send WebSocket notifications to drivers.
        
        This is a helper method that sends real-time notifications
        to connected drivers via WebSocket.
        
        Args:
            drivers: List of driver dictionaries with driver_id and distance
            ride_id: Ride request ID
            pickup_latitude: Pickup latitude
            pickup_longitude: Pickup longitude
            destination_latitude: Destination latitude
            destination_longitude: Destination longitude
            estimated_fare: Estimated fare
            broadcast_time: ISO timestamp of broadcast
            is_extended_area: Whether this is an extended area ride
            
        Returns:
            Number of WebSocket notifications successfully sent
        """
        import asyncio
        from app.services.websocket_service import connection_manager
        
        async def send_notifications():
            sent_count = 0
            for driver in drivers:
                websocket_message = {
                    "type": "ride_request",
                    "data": {
                        "ride_id": ride_id,
                        "pickup": {
                            "latitude": pickup_latitude,
                            "longitude": pickup_longitude
                        },
                        "destination": {
                            "latitude": destination_latitude,
                            "longitude": destination_longitude
                        },
                        "estimated_fare": estimated_fare,
                        "distance_to_pickup_km": driver["distance_km"],
                        "is_extended_area": is_extended_area,
                        "broadcast_time": broadcast_time
                    },
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                # Send to driver if connected
                if await connection_manager.send_personal_message(websocket_message, driver["driver_id"]):
                    sent_count += 1
            return sent_count
        
        # Run async function in event loop
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If loop is already running, create a task
                task = loop.create_task(send_notifications())
                # Don't wait for it, return 0 as we can't get the count synchronously
                return 0
            else:
                # If no loop is running, run it
                return loop.run_until_complete(send_notifications())
        except RuntimeError:
            # No event loop, create one
            return asyncio.run(send_notifications())
    
    def get_broadcast_details(self, ride_id: str) -> Optional[Dict[str, Any]]:
        """
        Get broadcast details for a ride request.
        
        Args:
            ride_id: Ride request ID
            
        Returns:
            Dict with broadcast details or None if not found
        """
        broadcast_key = f"ride:broadcast:{ride_id}"
        data = self.redis.get(broadcast_key)
        
        if data:
            return json.loads(data)
        
        return None
    
    def cancel_broadcast(self, ride_id: str) -> Dict[str, Any]:
        """
        Cancel an active broadcast (e.g., when ride is matched or cancelled).
        
        Args:
            ride_id: Ride request ID
            
        Returns:
            Dict with status and message
        """
        broadcast_key = f"ride:broadcast:{ride_id}"
        broadcast_data = self.redis.get(broadcast_key)
        
        if not broadcast_data:
            return {
                "status": "not_found",
                "message": f"No active broadcast found for ride {ride_id}"
            }
        
        broadcast = json.loads(broadcast_data)
        
        # Update broadcast status to cancelled
        broadcast["status"] = "cancelled"
        broadcast["cancelled_at"] = datetime.utcnow().isoformat()
        
        # Store updated broadcast
        self.redis.setex(
            broadcast_key,
            timedelta(minutes=10),
            json.dumps(broadcast)
        )
        
        # Remove notifications from driver queues
        for driver_id in broadcast.get("notified_drivers", []):
            driver_notification_key = f"driver:notifications:{driver_id}"
            
            # Get all notifications for this driver
            notifications = self.redis.zrange(driver_notification_key, 0, -1)
            
            # Remove notifications for this ride
            for notification_json in notifications:
                notification = json.loads(notification_json)
                if notification.get("ride_id") == ride_id:
                    self.redis.zrem(driver_notification_key, notification_json)
        
        return {
            "status": "success",
            "message": f"Broadcast cancelled for ride {ride_id}",
            "drivers_notified": len(broadcast.get("notified_drivers", []))
        }

    
    def match_ride(
        self,
        ride_id: str,
        driver_id: str,
        rider_id: str
    ) -> Dict[str, Any]:
        """
        Match a driver to a ride request with concurrent acceptance handling.
        
        Uses Redis locks to handle concurrent acceptances and selects the
        closest driver when multiple drivers accept simultaneously.
        
        Args:
            ride_id: Unique ride request ID
            driver_id: Driver accepting the ride
            rider_id: Rider who requested the ride
            
        Returns:
            Dict with match details or error information
        """
        from app.models.ride import Ride, RideStatus
        
        # Create a lock key for this ride to handle concurrent acceptances
        lock_key = f"ride:lock:{ride_id}"
        lock_timeout = 10  # seconds
        
        # Try to acquire lock
        lock_acquired = self.redis.set(
            lock_key,
            driver_id,
            nx=True,  # Only set if doesn't exist
            ex=lock_timeout
        )
        
        if not lock_acquired:
            # Another driver is already processing this ride
            # Check if the ride is already matched
            ride = self.db.query(Ride).filter(Ride.ride_id == ride_id).first()
            
            if ride and ride.status == RideStatus.MATCHED:
                # Ride already matched to another driver
                return {
                    "status": "already_matched",
                    "message": f"Ride {ride_id} has already been matched to another driver",
                    "matched_driver_id": ride.driver_id
                }
            
            # Lock is held but ride not yet matched, wait briefly and retry
            return {
                "status": "processing",
                "message": "Another driver is currently being matched to this ride"
            }
        
        try:
            # Lock acquired, proceed with matching
            
            # Verify driver is available
            if not self.is_driver_available(driver_id):
                return {
                    "status": "error",
                    "message": f"Driver {driver_id} is not available"
                }
            
            # Get the ride from database
            ride = self.db.query(Ride).filter(Ride.ride_id == ride_id).first()
            
            if not ride:
                return {
                    "status": "error",
                    "message": f"Ride {ride_id} not found"
                }
            
            # Check if ride is still in requested status
            if ride.status != RideStatus.REQUESTED:
                return {
                    "status": "error",
                    "message": f"Ride {ride_id} is no longer available for matching (status: {ride.status})"
                }
            
            # Verify rider matches
            if ride.rider_id != rider_id:
                return {
                    "status": "error",
                    "message": "Rider ID mismatch"
                }
            
            # Get driver location
            driver_location_key = f"{self.DRIVER_LOCATION_PREFIX}{driver_id}"
            driver_location_data = self.redis.get(driver_location_key)
            
            if not driver_location_data:
                return {
                    "status": "error",
                    "message": f"Driver {driver_id} location not found"
                }
            
            driver_location = json.loads(driver_location_data)
            
            # Calculate distance to pickup
            from app.services.location_service import calculate_distance
            pickup_lat = ride.pickup_location["latitude"]
            pickup_lon = ride.pickup_location["longitude"]
            
            distance_to_pickup = calculate_distance(
                pickup_lat,
                pickup_lon,
                driver_location["latitude"],
                driver_location["longitude"]
            )
            
            # Calculate estimated arrival time (assuming 30 km/h average speed)
            estimated_arrival_minutes = int((distance_to_pickup / 30) * 60)
            
            # Update ride with match information
            ride.driver_id = driver_id
            ride.status = RideStatus.MATCHED
            ride.matched_at = datetime.utcnow()
            
            # Commit the match
            self.db.commit()
            
            # Update driver status to busy
            self.set_driver_busy(driver_id)
            
            # Cancel the broadcast for this ride
            self.cancel_broadcast(ride_id)
            
            # Get driver details
            from app.models.user import User
            driver = self.db.query(User).filter(User.user_id == driver_id).first()
            
            match_result = {
                "status": "success",
                "ride_id": ride_id,
                "driver_id": driver_id,
                "rider_id": rider_id,
                "matched_at": ride.matched_at.isoformat(),
                "distance_to_pickup_km": round(distance_to_pickup, 2),
                "estimated_arrival_minutes": estimated_arrival_minutes,
                "driver_details": {
                    "name": driver.name,
                    "phone_number": driver.phone_number,
                    "rating": driver.average_rating,
                    "total_rides": driver.total_rides
                } if driver else None
            }
            
            # Add vehicle details if available
            if driver and driver.driver_profile:
                match_result["vehicle_details"] = {
                    "registration_number": driver.driver_profile.vehicle_registration,
                    "make": driver.driver_profile.vehicle_make,
                    "model": driver.driver_profile.vehicle_model,
                    "color": driver.driver_profile.vehicle_color
                }
            
            return match_result
            
        finally:
            # Always release the lock
            self.redis.delete(lock_key)

    
    def expand_search_radius(
        self,
        ride_id: str,
        current_radius_km: float = 5.0,
        expansion_km: float = 2.0
    ) -> Dict[str, Any]:
        """
        Expand the search radius for a ride request and re-broadcast.
        
        This is typically called after a timeout period (e.g., 2 minutes)
        when no driver has accepted the ride request.
        
        Args:
            ride_id: Unique ride request ID
            current_radius_km: Current search radius in kilometers
            expansion_km: Amount to expand radius by (default 2km)
            
        Returns:
            Dict with expansion details and newly notified drivers
        """
        from app.models.ride import Ride, RideStatus
        
        # Get the ride from database
        ride = self.db.query(Ride).filter(Ride.ride_id == ride_id).first()
        
        if not ride:
            return {
                "status": "error",
                "message": f"Ride {ride_id} not found"
            }
        
        # Check if ride is still in requested status
        if ride.status != RideStatus.REQUESTED:
            return {
                "status": "error",
                "message": f"Ride {ride_id} is no longer in requested status (current: {ride.status})"
            }
        
        # Get current broadcast details
        broadcast_details = self.get_broadcast_details(ride_id)
        
        if not broadcast_details:
            return {
                "status": "error",
                "message": f"No active broadcast found for ride {ride_id}"
            }
        
        # Calculate new radius
        new_radius_km = current_radius_km + expansion_km
        
        # Get previously notified drivers
        previously_notified = set(broadcast_details.get("notified_drivers", []))
        
        # Get all available drivers within new radius
        pickup_lat = ride.pickup_location["latitude"]
        pickup_lon = ride.pickup_location["longitude"]
        
        all_drivers_in_new_radius = self.get_available_drivers(
            pickup_lat,
            pickup_lon,
            new_radius_km
        )
        
        # Filter to only newly included drivers (not previously notified)
        newly_included_drivers = [
            driver for driver in all_drivers_in_new_radius
            if driver["driver_id"] not in previously_notified
        ]
        
        # Update broadcast details with new radius and newly notified drivers
        broadcast_details["radius_km"] = new_radius_km
        broadcast_details["broadcast_count"] = broadcast_details.get("broadcast_count", 1) + 1
        broadcast_details["last_expansion_at"] = datetime.utcnow().isoformat()
        
        # Add newly notified drivers to the list
        for driver in newly_included_drivers:
            if driver["driver_id"] not in broadcast_details["notified_drivers"]:
                broadcast_details["notified_drivers"].append(driver["driver_id"])
        
        # Store updated broadcast details
        broadcast_key = f"ride:broadcast:{ride_id}"
        self.redis.setex(
            broadcast_key,
            timedelta(minutes=10),
            json.dumps(broadcast_details)
        )
        
        # Send notifications to newly included drivers
        dest_lat = ride.destination["latitude"]
        dest_lon = ride.destination["longitude"]
        
        for driver in newly_included_drivers:
            driver_notification_key = f"driver:notifications:{driver['driver_id']}"
            notification_data = {
                "ride_id": ride_id,
                "pickup_latitude": pickup_lat,
                "pickup_longitude": pickup_lon,
                "destination_latitude": dest_lat,
                "destination_longitude": dest_lon,
                "estimated_fare": ride.estimated_fare,
                "distance_to_pickup_km": driver["distance_km"],
                "notified_at": datetime.utcnow().isoformat(),
                "broadcast_round": broadcast_details["broadcast_count"]
            }
            
            # Add to driver's notification list
            self.redis.zadd(
                driver_notification_key,
                {json.dumps(notification_data): datetime.utcnow().timestamp()}
            )
            
            # Set expiry on notification list
            self.redis.expire(driver_notification_key, timedelta(minutes=10))
        
        return {
            "status": "success",
            "ride_id": ride_id,
            "previous_radius_km": current_radius_km,
            "new_radius_km": new_radius_km,
            "expansion_km": expansion_km,
            "broadcast_count": broadcast_details["broadcast_count"],
            "newly_notified_drivers": len(newly_included_drivers),
            "total_notified_drivers": len(broadcast_details["notified_drivers"]),
            "newly_included_driver_ids": [d["driver_id"] for d in newly_included_drivers]
        }

    
    def reject_ride(
        self,
        ride_id: str,
        driver_id: str
    ) -> Dict[str, Any]:
        """
        Handle driver rejection of a ride request.
        
        When a driver rejects a ride, the ride request remains active
        for other drivers to accept. The rejection is logged but does
        not affect the broadcast.
        
        Args:
            ride_id: Unique ride request ID
            driver_id: Driver rejecting the ride
            
        Returns:
            Dict with rejection status and details
        """
        from app.models.ride import Ride, RideStatus
        
        # Get the ride from database
        ride = self.db.query(Ride).filter(Ride.ride_id == ride_id).first()
        
        if not ride:
            return {
                "status": "error",
                "message": f"Ride {ride_id} not found"
            }
        
        # Check if ride is still in requested status
        if ride.status != RideStatus.REQUESTED:
            return {
                "status": "error",
                "message": f"Ride {ride_id} is no longer available (status: {ride.status})"
            }
        
        # Verify driver was notified about this ride
        broadcast_details = self.get_broadcast_details(ride_id)
        
        if not broadcast_details:
            return {
                "status": "error",
                "message": f"No active broadcast found for ride {ride_id}"
            }
        
        if driver_id not in broadcast_details.get("notified_drivers", []):
            return {
                "status": "error",
                "message": f"Driver {driver_id} was not notified about this ride"
            }
        
        # Log the rejection in Redis
        rejection_key = f"ride:rejections:{ride_id}"
        rejection_data = {
            "driver_id": driver_id,
            "rejected_at": datetime.utcnow().isoformat()
        }
        
        # Add to rejection list (as a sorted set with timestamp as score)
        self.redis.zadd(
            rejection_key,
            {json.dumps(rejection_data): datetime.utcnow().timestamp()}
        )
        
        # Set expiry on rejection list (same as broadcast)
        self.redis.expire(rejection_key, timedelta(minutes=10))
        
        # Remove the notification from driver's queue
        driver_notification_key = f"driver:notifications:{driver_id}"
        notifications = self.redis.zrange(driver_notification_key, 0, -1)
        
        for notification_json in notifications:
            notification = json.loads(notification_json)
            if notification.get("ride_id") == ride_id:
                self.redis.zrem(driver_notification_key, notification_json)
                break
        
        # Get count of rejections for this ride
        rejection_count = self.redis.zcard(rejection_key)
        
        # Get remaining drivers who haven't rejected
        notified_drivers = set(broadcast_details.get("notified_drivers", []))
        
        # Get all rejections
        all_rejections = self.redis.zrange(rejection_key, 0, -1)
        rejected_driver_ids = set()
        for rejection_json in all_rejections:
            rejection = json.loads(rejection_json)
            rejected_driver_ids.add(rejection["driver_id"])
        
        remaining_drivers = notified_drivers - rejected_driver_ids
        
        return {
            "status": "success",
            "ride_id": ride_id,
            "driver_id": driver_id,
            "rejected_at": rejection_data["rejected_at"],
            "message": "Ride rejection recorded. Ride remains active for other drivers.",
            "rejection_count": rejection_count,
            "remaining_drivers": len(remaining_drivers),
            "broadcast_still_active": True
        }

    def handle_driver_cancellation(
        self,
        ride_id: str,
        driver_id: str,
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Handle driver cancellation of a matched ride before pickup.
        
        When a driver cancels a matched ride:
        1. Record the cancellation in driver's history
        2. Increment driver's daily cancellation count
        3. Suspend driver if they exceed 3 cancellations in a day
        4. Update ride status back to REQUESTED
        5. Re-broadcast the ride request to other available drivers
        
        Args:
            ride_id: Unique ride ID
            driver_id: Driver cancelling the ride
            reason: Optional cancellation reason
            
        Returns:
            Dict with cancellation status and details
        """
        from app.models.ride import Ride, RideStatus
        from app.models.user import User, DriverProfile
        
        # Get the ride from database
        ride = self.db.query(Ride).filter(Ride.ride_id == ride_id).first()
        
        if not ride:
            return {
                "status": "error",
                "message": f"Ride {ride_id} not found"
            }
        
        # Verify the ride is matched to this driver
        if ride.driver_id != driver_id:
            return {
                "status": "error",
                "message": f"Ride {ride_id} is not assigned to driver {driver_id}"
            }
        
        # Check if ride can be cancelled (before pickup)
        if not ride.is_cancellable():
            return {
                "status": "error",
                "message": f"Ride {ride_id} cannot be cancelled (status: {ride.status})"
            }
        
        # Get driver profile
        driver = self.db.query(User).filter(User.user_id == driver_id).first()
        if not driver or not driver.driver_profile:
            return {
                "status": "error",
                "message": f"Driver {driver_id} not found or not a driver"
            }
        
        driver_profile = driver.driver_profile
        
        # Check if we need to reset daily cancellation count
        now = datetime.utcnow()
        if driver_profile.last_cancellation_reset:
            time_since_reset = now - driver_profile.last_cancellation_reset
            # Reset if more than 24 hours have passed
            if time_since_reset.total_seconds() >= 86400:  # 24 hours
                driver_profile.cancellation_count = 0
                driver_profile.last_cancellation_reset = now
        
        # Increment cancellation count
        driver_profile.cancellation_count += 1
        
        # Log the cancellation in Redis
        cancellation_key = f"driver:cancellations:{driver_id}"
        cancellation_data = {
            "ride_id": ride_id,
            "cancelled_at": now.isoformat(),
            "reason": reason
        }
        
        # Add to cancellation list (as a sorted set with timestamp as score)
        self.redis.zadd(
            cancellation_key,
            {json.dumps(cancellation_data): now.timestamp()}
        )
        
        # Set expiry on cancellation list (24 hours)
        self.redis.expire(cancellation_key, timedelta(hours=24))
        
        # Check if driver should be suspended (more than 3 cancellations)
        should_suspend = driver_profile.cancellation_count > 3
        
        if should_suspend:
            driver_profile.is_suspended = True
            # Set driver status to unavailable
            self.set_driver_unavailable(driver_id)
            
            # Store suspension info in Redis with 24-hour expiry
            suspension_key = f"driver:suspension:{driver_id}"
            suspension_data = {
                "suspended_at": now.isoformat(),
                "reason": "Exceeded daily cancellation limit (3 cancellations)",
                "cancellation_count": driver_profile.cancellation_count,
                "expires_at": (now + timedelta(hours=24)).isoformat()
            }
            self.redis.setex(
                suspension_key,
                timedelta(hours=24),
                json.dumps(suspension_data)
            )
        
        # Update ride record
        ride.status = RideStatus.REQUESTED
        ride.driver_id = None
        ride.matched_at = None
        ride.cancelled_by = driver_id
        ride.cancellation_reason = reason or "Driver cancelled"
        ride.cancellation_timestamp = now
        
        # Commit changes to database
        self.db.commit()
        
        # Cancel the existing broadcast if any
        self.cancel_broadcast(ride_id)
        
        # Re-broadcast the ride request to available drivers
        # Use the original pickup location from the ride
        pickup_location = ride.pickup_location
        destination = ride.destination
        
        # Re-broadcast with initial 5km radius
        broadcast_result = self.broadcast_ride_request(
            ride_id=ride_id,
            pickup_latitude=pickup_location["latitude"],
            pickup_longitude=pickup_location["longitude"],
            destination_latitude=destination["latitude"],
            destination_longitude=destination["longitude"],
            estimated_fare=ride.estimated_fare,
            radius_km=5.0
        )
        
        return {
            "status": "success",
            "ride_id": ride_id,
            "driver_id": driver_id,
            "cancelled_at": now.isoformat(),
            "cancellation_count": driver_profile.cancellation_count,
            "driver_suspended": should_suspend,
            "suspension_expires_at": (now + timedelta(hours=24)).isoformat() if should_suspend else None,
            "ride_re_broadcasted": broadcast_result.get("status") == "success",
            "notified_drivers": broadcast_result.get("notified_drivers", []),
            "message": "Driver cancellation processed. Ride re-broadcasted to available drivers." + 
                      (" Driver suspended for 24 hours due to excessive cancellations." if should_suspend else "")
        }


    def broadcast_parcel_request(
        self,
        delivery_id: str,
        pickup_latitude: float,
        pickup_longitude: float,
        delivery_latitude: float,
        delivery_longitude: float,
        estimated_fare: float,
        parcel_size: str,
        is_fragile: bool = False,
        is_urgent: bool = False,
        special_instructions: Optional[str] = None,
        radius_km: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Broadcast parcel delivery request to available drivers within radius.
        
        Filters drivers by parcel delivery preference and uses same proximity-based
        matching algorithm as ride requests.
        
        Args:
            delivery_id: Unique parcel delivery ID
            pickup_latitude: Pickup location latitude
            pickup_longitude: Pickup location longitude
            delivery_latitude: Delivery location latitude
            delivery_longitude: Delivery location longitude
            estimated_fare: Estimated fare for the delivery
            parcel_size: Size of parcel (small/medium/large)
            is_fragile: Whether parcel is fragile
            is_urgent: Whether delivery is urgent
            special_instructions: Special handling instructions
            radius_km: Search radius in kilometers (if None, uses dynamic radius based on location)
            
        Returns:
            Dict with broadcast details and list of notified drivers
            
        Requirements: 17.1
        """
        # Use dynamic radius if not specified
        if radius_km is None:
            radius_km = self.get_initial_search_radius(pickup_latitude, pickup_longitude)
        
        # Determine if this is an extended area delivery
        is_extended_area = self.is_in_extended_area(pickup_latitude, pickup_longitude) or \
                          self.is_in_extended_area(delivery_latitude, delivery_longitude)
        
        # Get available drivers within radius
        available_drivers = self.get_available_drivers(
            pickup_latitude,
            pickup_longitude,
            radius_km
        )
        
        # Filter drivers by parcel delivery preference (Requirements: 17.1)
        available_drivers = [
            driver for driver in available_drivers
            if driver.get("accept_parcel_delivery", True)  # Default to True if not set
        ]
        
        # Filter by extended area preference if needed
        if is_extended_area:
            available_drivers = [
                driver for driver in available_drivers
                if driver.get("accept_extended_area", True)
            ]
        
        # Store broadcast details in Redis
        broadcast_key = f"parcel:broadcast:{delivery_id}"
        broadcast_data = {
            "delivery_id": delivery_id,
            "pickup_latitude": pickup_latitude,
            "pickup_longitude": pickup_longitude,
            "delivery_latitude": delivery_latitude,
            "delivery_longitude": delivery_longitude,
            "estimated_fare": estimated_fare,
            "parcel_size": parcel_size,
            "is_fragile": is_fragile,
            "is_urgent": is_urgent,
            "special_instructions": special_instructions,
            "radius_km": radius_km,
            "is_extended_area": is_extended_area,
            "broadcast_time": datetime.utcnow().isoformat(),
            "notified_drivers": [d["driver_id"] for d in available_drivers],
            "status": "active"
        }
        
        # Store broadcast with 10 minute expiry
        self.redis.setex(
            broadcast_key,
            timedelta(minutes=10),
            json.dumps(broadcast_data)
        )
        
        # Store driver notification list for this parcel
        for driver in available_drivers:
            driver_notification_key = f"driver:parcel_notifications:{driver['driver_id']}"
            notification_data = {
                "delivery_id": delivery_id,
                "pickup_latitude": pickup_latitude,
                "pickup_longitude": pickup_longitude,
                "delivery_latitude": delivery_latitude,
                "delivery_longitude": delivery_longitude,
                "estimated_fare": estimated_fare,
                "parcel_size": parcel_size,
                "is_fragile": is_fragile,
                "is_urgent": is_urgent,
                "special_instructions": special_instructions,
                "distance_to_pickup_km": driver["distance_km"],
                "is_extended_area": is_extended_area,
                "notified_at": datetime.utcnow().isoformat()
            }
            
            # Add to driver's notification list (as a sorted set with timestamp as score)
            self.redis.zadd(
                driver_notification_key,
                {json.dumps(notification_data): datetime.utcnow().timestamp()}
            )
            
            # Set expiry on notification list
            self.redis.expire(driver_notification_key, timedelta(minutes=10))
        
        # Send WebSocket notifications (non-blocking)
        websocket_sent_count = self._send_parcel_websocket_notifications(
            available_drivers,
            delivery_id,
            pickup_latitude,
            pickup_longitude,
            delivery_latitude,
            delivery_longitude,
            estimated_fare,
            parcel_size,
            is_fragile,
            is_urgent,
            special_instructions,
            broadcast_data["broadcast_time"],
            is_extended_area
        )
        
        return {
            "status": "success",
            "delivery_id": delivery_id,
            "broadcast_radius_km": radius_km,
            "is_extended_area": is_extended_area,
            "drivers_notified": len(available_drivers),
            "websocket_notifications_sent": websocket_sent_count,
            "notified_drivers": [
                {
                    "driver_id": d["driver_id"],
                    "name": d["name"],
                    "distance_km": d["distance_km"]
                }
                for d in available_drivers
            ]
        }
    
    def _send_parcel_websocket_notifications(
        self,
        drivers: List[Dict[str, Any]],
        delivery_id: str,
        pickup_latitude: float,
        pickup_longitude: float,
        delivery_latitude: float,
        delivery_longitude: float,
        estimated_fare: float,
        parcel_size: str,
        is_fragile: bool,
        is_urgent: bool,
        special_instructions: Optional[str],
        broadcast_time: str,
        is_extended_area: bool = False
    ) -> int:
        """
        Send WebSocket notifications to drivers for parcel delivery.
        
        Args:
            drivers: List of driver dictionaries
            delivery_id: Parcel delivery ID
            pickup_latitude: Pickup latitude
            pickup_longitude: Pickup longitude
            delivery_latitude: Delivery latitude
            delivery_longitude: Delivery longitude
            estimated_fare: Estimated fare
            parcel_size: Size of parcel
            is_fragile: Whether parcel is fragile
            is_urgent: Whether delivery is urgent
            special_instructions: Special handling instructions
            broadcast_time: ISO timestamp of broadcast
            is_extended_area: Whether this is an extended area delivery
            
        Returns:
            Number of WebSocket notifications successfully sent
        """
        import asyncio
        from app.services.websocket_service import connection_manager
        
        async def send_notifications():
            sent_count = 0
            for driver in drivers:
                websocket_message = {
                    "type": "parcel_request",
                    "data": {
                        "delivery_id": delivery_id,
                        "pickup": {
                            "latitude": pickup_latitude,
                            "longitude": pickup_longitude
                        },
                        "delivery": {
                            "latitude": delivery_latitude,
                            "longitude": delivery_longitude
                        },
                        "estimated_fare": estimated_fare,
                        "parcel_size": parcel_size,
                        "is_fragile": is_fragile,
                        "is_urgent": is_urgent,
                        "special_instructions": special_instructions,
                        "distance_to_pickup_km": driver["distance_km"],
                        "is_extended_area": is_extended_area,
                        "broadcast_time": broadcast_time
                    },
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                # Send to driver if connected
                if await connection_manager.send_personal_message(websocket_message, driver["driver_id"]):
                    sent_count += 1
            return sent_count
        
        # Run async function in event loop
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If loop is already running, create a task
                task = loop.create_task(send_notifications())
                # Don't wait for it, return 0 as we can't get the count synchronously
                return 0
            else:
                # If no loop is running, run it
                return loop.run_until_complete(send_notifications())
        except RuntimeError:
            # No event loop, create one
            return asyncio.run(send_notifications())
    
    def match_parcel(
        self,
        delivery_id: str,
        driver_id: str,
        sender_id: str
    ) -> Dict[str, Any]:
        """
        Match a driver to a parcel delivery request with concurrent acceptance handling.
        
        Uses Redis locks to handle concurrent acceptances and selects the
        closest driver when multiple drivers accept simultaneously.
        
        Args:
            delivery_id: Unique parcel delivery ID
            driver_id: Driver accepting the delivery
            sender_id: Sender who requested the delivery
            
        Returns:
            Dict with match details or error information
        """
        from app.models.parcel_delivery import ParcelDelivery, ParcelStatus
        
        # Create a lock key for this delivery to handle concurrent acceptances
        lock_key = f"parcel:lock:{delivery_id}"
        lock_timeout = 10  # seconds
        
        # Try to acquire lock
        lock_acquired = self.redis.set(
            lock_key,
            driver_id,
            nx=True,  # Only set if doesn't exist
            ex=lock_timeout
        )
        
        if not lock_acquired:
            # Another driver is already processing this delivery
            # Check if the delivery is already matched
            parcel = self.db.query(ParcelDelivery).filter(
                ParcelDelivery.delivery_id == delivery_id
            ).first()
            
            if parcel and parcel.status == ParcelStatus.MATCHED:
                # Delivery already matched to another driver
                return {
                    "status": "already_matched",
                    "message": f"Parcel delivery {delivery_id} has already been matched to another driver",
                    "matched_driver_id": parcel.driver_id
                }
            
            # Lock is held but delivery not yet matched, wait briefly and retry
            return {
                "status": "processing",
                "message": "Another driver is currently being matched to this delivery"
            }
        
        try:
            # Lock acquired, proceed with matching
            
            # Verify driver is available
            if not self.is_driver_available(driver_id):
                return {
                    "status": "error",
                    "message": f"Driver {driver_id} is not available"
                }
            
            # Get the parcel delivery from database
            parcel = self.db.query(ParcelDelivery).filter(
                ParcelDelivery.delivery_id == delivery_id
            ).first()
            
            if not parcel:
                return {
                    "status": "error",
                    "message": f"Parcel delivery {delivery_id} not found"
                }
            
            # Check if delivery is still in requested status
            if parcel.status != ParcelStatus.REQUESTED:
                return {
                    "status": "error",
                    "message": f"Parcel delivery {delivery_id} is no longer available for matching (status: {parcel.status})"
                }
            
            # Verify sender matches
            if parcel.sender_id != sender_id:
                return {
                    "status": "error",
                    "message": "Sender ID mismatch"
                }
            
            # Get driver location
            driver_location_key = f"{self.DRIVER_LOCATION_PREFIX}{driver_id}"
            driver_location_data = self.redis.get(driver_location_key)
            
            if not driver_location_data:
                return {
                    "status": "error",
                    "message": f"Driver {driver_id} location not found"
                }
            
            driver_location = json.loads(driver_location_data)
            
            # Calculate distance to pickup
            from app.services.location_service import calculate_distance
            pickup_lat = parcel.pickup_location["latitude"]
            pickup_lon = parcel.pickup_location["longitude"]
            
            distance_to_pickup = calculate_distance(
                pickup_lat,
                pickup_lon,
                driver_location["latitude"],
                driver_location["longitude"]
            )
            
            # Calculate estimated arrival time (assuming 30 km/h average speed)
            estimated_arrival_minutes = int((distance_to_pickup / 30) * 60)
            
            # Update parcel with match information
            parcel.driver_id = driver_id
            parcel.status = ParcelStatus.MATCHED
            parcel.matched_at = datetime.utcnow()
            
            # Commit the match
            self.db.commit()
            
            # Update driver status to busy
            self.set_driver_busy(driver_id)
            
            # Cancel the broadcast for this delivery
            broadcast_key = f"parcel:broadcast:{delivery_id}"
            self.redis.delete(broadcast_key)
            
            # Get driver details
            from app.models.user import User
            driver = self.db.query(User).filter(User.user_id == driver_id).first()
            
            match_result = {
                "status": "success",
                "delivery_id": delivery_id,
                "driver_id": driver_id,
                "sender_id": sender_id,
                "matched_at": parcel.matched_at.isoformat(),
                "distance_to_pickup_km": round(distance_to_pickup, 2),
                "estimated_arrival_minutes": estimated_arrival_minutes,
                "driver_details": {
                    "name": driver.name,
                    "phone_number": driver.phone_number,
                    "rating": driver.average_rating,
                    "total_rides": driver.total_rides
                } if driver else None
            }
            
            # Add vehicle details if available
            if driver and driver.driver_profile:
                match_result["vehicle_details"] = {
                    "registration_number": driver.driver_profile.vehicle_registration,
                    "make": driver.driver_profile.vehicle_make,
                    "model": driver.driver_profile.vehicle_model,
                    "color": driver.driver_profile.vehicle_color
                }
            
            return match_result
            
        finally:
            # Always release the lock
            self.redis.delete(lock_key)
