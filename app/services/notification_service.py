"""
Notification Service for sending SMS and in-app notifications.
Handles Twilio SMS integration and WebSocket notifications.
"""
from typing import Optional, Dict, Any, List
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

from app.config import settings


class NotificationService:
    """Service for managing notifications via SMS and WebSocket."""
    
    def __init__(self):
        """Initialize notification service with Twilio client."""
        self.twilio_client = None
        if settings.twilio_account_sid and settings.twilio_auth_token:
            self.twilio_client = Client(
                settings.twilio_account_sid,
                settings.twilio_auth_token
            )
        self.twilio_phone = settings.twilio_phone_number
    
    async def send_sms(
        self,
        phone_number: str,
        message: str
    ) -> Dict[str, Any]:
        """
        Send SMS notification via Twilio.
        
        Args:
            phone_number: Recipient phone number (E.164 format)
            message: SMS message content
            
        Returns:
            Dict with status and message details
        """
        if not self.twilio_client:
            return {
                "success": False,
                "error": "Twilio not configured"
            }
        
        try:
            sms = self.twilio_client.messages.create(
                body=message,
                from_=self.twilio_phone,
                to=phone_number
            )
            
            return {
                "success": True,
                "message_sid": sms.sid,
                "status": sms.status,
                "to": phone_number
            }
        except TwilioRestException as e:
            return {
                "success": False,
                "error": str(e),
                "error_code": e.code
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def send_verification_code(
        self,
        phone_number: str,
        code: str
    ) -> Dict[str, Any]:
        """
        Send verification code via SMS.
        
        Args:
            phone_number: Recipient phone number
            code: Verification code
            
        Returns:
            Dict with status
        """
        message = f"Your verification code is: {code}. Valid for 10 minutes."
        return await self.send_sms(phone_number, message)
    
    async def send_in_app_notification(
        self,
        user_id: str,
        notification: Dict[str, Any],
        websocket_manager: Any
    ) -> bool:
        """
        Send in-app notification via WebSocket.
        
        Args:
            user_id: User identifier
            notification: Notification data
            websocket_manager: WebSocket connection manager
            
        Returns:
            True if sent successfully
        """
        try:
            await websocket_manager.send_to_user(user_id, notification)
            return True
        except Exception:
            return False
    
    async def send_dual_notification(
        self,
        user_id: str,
        phone_number: str,
        notification: Dict[str, Any],
        sms_message: str,
        websocket_manager: Any = None
    ) -> Dict[str, Any]:
        """
        Send notification via both SMS and in-app channels.
        Used for critical events.
        
        Args:
            user_id: User identifier
            phone_number: User phone number
            notification: In-app notification data
            sms_message: SMS message content
            websocket_manager: WebSocket connection manager (optional)
            
        Returns:
            Dict with status of both channels
        """
        results = {
            "sms": {"sent": False},
            "in_app": {"sent": False}
        }
        
        # Send SMS
        sms_result = await self.send_sms(phone_number, sms_message)
        results["sms"] = sms_result
        
        # Send in-app notification if WebSocket manager provided
        if websocket_manager:
            in_app_sent = await self.send_in_app_notification(
                user_id,
                notification,
                websocket_manager
            )
            results["in_app"]["sent"] = in_app_sent
        
        return results
    
    # Ride Event Notifications
    
    async def send_match_notification(
        self,
        rider_phone: str,
        driver_name: str,
        driver_phone: str,
        vehicle_info: Dict[str, str],
        driver_rating: float,
        eta_minutes: int,
        websocket_manager: Any = None,
        rider_id: str = None
    ) -> Dict[str, Any]:
        """
        Send ride match notification to rider.
        
        Args:
            rider_phone: Rider phone number
            driver_name: Driver name
            driver_phone: Driver phone number
            vehicle_info: Vehicle details (make, model, color, registration)
            driver_rating: Driver average rating
            eta_minutes: Estimated arrival time in minutes
            websocket_manager: WebSocket manager (optional)
            rider_id: Rider ID for in-app notification (optional)
            
        Returns:
            Notification result
        """
        # SMS message
        sms_message = (
            f"Ride matched! Driver: {driver_name} ({driver_rating}★). "
            f"Vehicle: {vehicle_info['color']} {vehicle_info['make']} {vehicle_info['model']} "
            f"({vehicle_info['registration']}). ETA: {eta_minutes} min. "
            f"Contact: {driver_phone}"
        )
        
        # In-app notification
        notification = {
            "type": "ride_matched",
            "title": "Ride Matched!",
            "message": f"Your driver {driver_name} is on the way",
            "data": {
                "driver_name": driver_name,
                "driver_phone": driver_phone,
                "driver_rating": driver_rating,
                "vehicle": vehicle_info,
                "eta_minutes": eta_minutes
            }
        }
        
        if websocket_manager and rider_id:
            return await self.send_dual_notification(
                rider_id,
                rider_phone,
                notification,
                sms_message,
                websocket_manager
            )
        else:
            return await self.send_sms(rider_phone, sms_message)
    
    async def send_acceptance_notification(
        self,
        driver_phone: str,
        pickup_address: str,
        pickup_lat: float,
        pickup_lon: float,
        estimated_fare: float,
        websocket_manager: Any = None,
        driver_id: str = None
    ) -> Dict[str, Any]:
        """
        Send ride acceptance notification to driver.
        
        Args:
            driver_phone: Driver phone number
            pickup_address: Pickup location address
            pickup_lat: Pickup latitude
            pickup_lon: Pickup longitude
            estimated_fare: Estimated fare
            websocket_manager: WebSocket manager (optional)
            driver_id: Driver ID for in-app notification (optional)
            
        Returns:
            Notification result
        """
        sms_message = (
            f"Ride accepted! Pickup: {pickup_address}. "
            f"Estimated fare: ₹{estimated_fare:.2f}. "
            f"Navigate to: {pickup_lat},{pickup_lon}"
        )
        
        notification = {
            "type": "ride_accepted",
            "title": "Ride Accepted",
            "message": f"Navigate to pickup location",
            "data": {
                "pickup_address": pickup_address,
                "pickup_location": {
                    "latitude": pickup_lat,
                    "longitude": pickup_lon
                },
                "estimated_fare": estimated_fare
            }
        }
        
        if websocket_manager and driver_id:
            return await self.send_dual_notification(
                driver_id,
                driver_phone,
                notification,
                sms_message,
                websocket_manager
            )
        else:
            return await self.send_sms(driver_phone, sms_message)
    
    async def send_arrival_notification(
        self,
        rider_phone: str,
        driver_name: str,
        websocket_manager: Any = None,
        rider_id: str = None
    ) -> Dict[str, Any]:
        """
        Send driver arrival notification to rider.
        
        Args:
            rider_phone: Rider phone number
            driver_name: Driver name
            websocket_manager: WebSocket manager (optional)
            rider_id: Rider ID for in-app notification (optional)
            
        Returns:
            Notification result
        """
        sms_message = f"Your driver {driver_name} has arrived at the pickup location!"
        
        notification = {
            "type": "driver_arrived",
            "title": "Driver Arrived",
            "message": f"{driver_name} is waiting for you",
            "data": {
                "driver_name": driver_name
            }
        }
        
        if websocket_manager and rider_id:
            return await self.send_dual_notification(
                rider_id,
                rider_phone,
                notification,
                sms_message,
                websocket_manager
            )
        else:
            return await self.send_sms(rider_phone, sms_message)
    
    async def send_completion_notification(
        self,
        user_phone: str,
        final_fare: float,
        websocket_manager: Any = None,
        user_id: str = None
    ) -> Dict[str, Any]:
        """
        Send ride completion notification with rating prompt.
        
        Args:
            user_phone: User phone number
            final_fare: Final fare amount
            websocket_manager: WebSocket manager (optional)
            user_id: User ID for in-app notification (optional)
            
        Returns:
            Notification result
        """
        sms_message = (
            f"Ride completed! Fare: ₹{final_fare:.2f}. "
            f"Please rate your experience."
        )
        
        notification = {
            "type": "ride_completed",
            "title": "Ride Completed",
            "message": "Please rate your experience",
            "data": {
                "final_fare": final_fare,
                "prompt_rating": True
            }
        }
        
        if websocket_manager and user_id:
            return await self.send_dual_notification(
                user_id,
                user_phone,
                notification,
                sms_message,
                websocket_manager
            )
        else:
            return await self.send_sms(user_phone, sms_message)
    
    async def send_payment_receipt_notification(
        self,
        rider_phone: str,
        transaction_id: str,
        amount: float,
        websocket_manager: Any = None,
        rider_id: str = None
    ) -> Dict[str, Any]:
        """
        Send payment receipt notification to rider.
        
        Args:
            rider_phone: Rider phone number
            transaction_id: Transaction identifier
            amount: Payment amount
            websocket_manager: WebSocket manager (optional)
            rider_id: Rider ID for in-app notification (optional)
            
        Returns:
            Notification result
        """
        sms_message = (
            f"Payment successful! Amount: ₹{amount:.2f}. "
            f"Transaction ID: {transaction_id}. "
            f"Receipt available in app."
        )
        
        notification = {
            "type": "payment_success",
            "title": "Payment Successful",
            "message": f"₹{amount:.2f} paid successfully",
            "data": {
                "transaction_id": transaction_id,
                "amount": amount
            }
        }
        
        if websocket_manager and rider_id:
            return await self.send_dual_notification(
                rider_id,
                rider_phone,
                notification,
                sms_message,
                websocket_manager
            )
        else:
            return await self.send_sms(rider_phone, sms_message)
    
    async def send_cancellation_notification(
        self,
        user_phone: str,
        cancelled_by: str,
        cancellation_fee: float = 0,
        websocket_manager: Any = None,
        user_id: str = None
    ) -> Dict[str, Any]:
        """
        Send ride cancellation notification.
        
        Args:
            user_phone: User phone number
            cancelled_by: Who cancelled (rider/driver)
            cancellation_fee: Cancellation fee if applicable
            websocket_manager: WebSocket manager (optional)
            user_id: User ID for in-app notification (optional)
            
        Returns:
            Notification result
        """
        if cancellation_fee > 0:
            sms_message = (
                f"Ride cancelled by {cancelled_by}. "
                f"Cancellation fee: ₹{cancellation_fee:.2f}"
            )
        else:
            sms_message = f"Ride cancelled by {cancelled_by}."
        
        notification = {
            "type": "ride_cancelled",
            "title": "Ride Cancelled",
            "message": f"Cancelled by {cancelled_by}",
            "data": {
                "cancelled_by": cancelled_by,
                "cancellation_fee": cancellation_fee
            }
        }
        
        if websocket_manager and user_id:
            return await self.send_dual_notification(
                user_id,
                user_phone,
                notification,
                sms_message,
                websocket_manager
            )
        else:
            return await self.send_sms(user_phone, sms_message)
