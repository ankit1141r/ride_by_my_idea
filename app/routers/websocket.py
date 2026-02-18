"""
WebSocket router for real-time communication.

Handles WebSocket connections with JWT authentication.
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, status
from fastapi.exceptions import WebSocketException
from typing import Optional
from datetime import datetime
import logging
import json
from app.services.websocket_service import connection_manager
from app.utils.jwt import decode_access_token

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ws", tags=["websocket"])


@router.websocket("")
async def websocket_endpoint(
    websocket: WebSocket,
    token: Optional[str] = Query(None)
):
    """
    WebSocket endpoint for real-time communication.
    
    Requires JWT token for authentication passed as query parameter.
    
    Query Parameters:
        token: JWT authentication token
    
    Connection Flow:
        1. Client connects with JWT token
        2. Server validates token and extracts user info
        3. Connection is registered in connection manager
        4. Server listens for messages from client
        5. On disconnect, connection is removed from manager
    
    Message Format (from client):
        {
            "type": "message_type",
            "data": {...}
        }
    
    Message Format (to client):
        {
            "type": "message_type",
            "data": {...},
            "timestamp": "ISO 8601 timestamp"
        }
    """
    # Validate token before accepting connection
    if not token:
        logger.warning("WebSocket connection attempt without token")
        raise WebSocketException(
            code=status.WS_1008_POLICY_VIOLATION,
            reason="Authentication token required"
        )
    
    try:
        # Decode and validate JWT token
        payload = decode_access_token(token)
        
        if not payload:
            logger.warning("Invalid or expired token")
            raise WebSocketException(
                code=status.WS_1008_POLICY_VIOLATION,
                reason="Invalid or expired authentication token"
            )
        
        user_id = payload.get("user_id")
        user_type = payload.get("user_type")
        
        if not user_id or not user_type:
            logger.warning(f"Invalid token payload: {payload}")
            raise WebSocketException(
                code=status.WS_1008_POLICY_VIOLATION,
                reason="Invalid authentication token"
            )
        
        # Accept connection and register in manager
        await connection_manager.connect(websocket, user_id, user_type)
        
        # Send connection confirmation
        await websocket.send_json({
            "type": "connection_established",
            "data": {
                "user_id": user_id,
                "user_type": user_type,
                "message": "WebSocket connection established successfully"
            }
        })
        
        try:
            # Listen for messages from client
            while True:
                # Receive message from client
                data = await websocket.receive_text()
                
                try:
                    message = json.loads(data)
                    message_type = message.get("type")
                    message_data = message.get("data", {})
                    
                    logger.debug(f"Received message from {user_id}: type={message_type}")
                    
                    # Handle different message types
                    if message_type == "ping":
                        # Respond to ping with pong
                        await websocket.send_json({
                            "type": "pong",
                            "data": {"timestamp": message_data.get("timestamp")}
                        })
                    
                    elif message_type == "driver_location_update":
                        # Driver sending location update
                        latitude = message_data.get("latitude")
                        longitude = message_data.get("longitude")
                        accuracy = message_data.get("accuracy")
                        ride_id = message_data.get("ride_id")
                        
                        if latitude is None or longitude is None:
                            await websocket.send_json({
                                "type": "error",
                                "data": {
                                    "message": "Missing latitude or longitude in location update"
                                }
                            })
                            continue
                        
                        logger.debug(f"Driver {user_id} location update: lat={latitude}, lon={longitude}")
                        
                        # Import here to avoid circular dependency
                        from app.config import get_mongodb
                        from app.services.location_service import LocationService
                        from app.database import get_db
                        from app.models.ride import Ride
                        
                        # Get MongoDB database
                        mongodb = get_mongodb()
                        location_service = LocationService(mongodb)
                        
                        try:
                            # Store location in MongoDB
                            location = await location_service.update_driver_location(
                                driver_id=user_id,
                                latitude=latitude,
                                longitude=longitude,
                                accuracy=accuracy
                            )
                            
                            # Send acknowledgment to driver
                            await websocket.send_json({
                                "type": "location_update_ack",
                                "data": {
                                    "received": True,
                                    "timestamp": location.timestamp.isoformat()
                                }
                            })
                            
                            # If driver has an active ride, broadcast location to rider
                            if ride_id:
                                db = next(get_db())
                                try:
                                    # Get ride details to find rider
                                    ride = db.query(Ride).filter(
                                        Ride.ride_id == ride_id,
                                        Ride.driver_id == user_id,
                                        Ride.status.in_(["matched", "driver_arriving", "in_progress"])
                                    ).first()
                                    
                                    if ride:
                                        # Broadcast location to rider
                                        rider_location_update = {
                                            "type": "driver_location_update",
                                            "data": {
                                                "ride_id": ride_id,
                                                "driver_id": user_id,
                                                "latitude": latitude,
                                                "longitude": longitude,
                                                "accuracy": accuracy,
                                                "timestamp": location.timestamp.isoformat()
                                            },
                                            "timestamp": datetime.utcnow().isoformat()
                                        }
                                        await connection_manager.send_personal_message(
                                            rider_location_update,
                                            ride.rider_id
                                        )
                                        
                                        logger.debug(f"Location update broadcast to rider {ride.rider_id}")
                                        
                                        # Check proximity to pickup location if driver is arriving
                                        if ride.status == "driver_arriving":
                                            from app.services.location_service import calculate_distance
                                            
                                            # Extract pickup coordinates from JSON
                                            pickup_lat = ride.pickup_location.get("latitude")
                                            pickup_lon = ride.pickup_location.get("longitude")
                                            
                                            if pickup_lat and pickup_lon:
                                                # Calculate distance to pickup
                                                distance_km = calculate_distance(
                                                    latitude, longitude,
                                                    pickup_lat, pickup_lon
                                                )
                                                distance_meters = distance_km * 1000
                                                
                                                # If within 500m, send proximity notification
                                                if distance_meters <= 500:
                                                    proximity_notification = {
                                                        "type": "driver_nearby",
                                                        "data": {
                                                            "ride_id": ride_id,
                                                            "driver_id": user_id,
                                                            "distance_meters": round(distance_meters, 2),
                                                            "message": "Your driver is nearby and will arrive soon"
                                                        },
                                                        "timestamp": datetime.utcnow().isoformat()
                                                    }
                                                    await connection_manager.send_personal_message(
                                                        proximity_notification,
                                                        ride.rider_id
                                                    )
                                                    
                                                    logger.info(f"Proximity notification sent to rider {ride.rider_id}: {distance_meters}m")
                                finally:
                                    db.close()
                        
                        except Exception as e:
                            logger.error(f"Error processing location update: {e}")
                            await websocket.send_json({
                                "type": "error",
                                "data": {
                                    "message": f"Error processing location update: {str(e)}"
                                }
                            })
                    
                    elif message_type == "ride_accept":
                        # Driver accepting a ride
                        ride_id = message_data.get("ride_id")
                        rider_id = message_data.get("rider_id")
                        
                        if not ride_id or not rider_id:
                            await websocket.send_json({
                                "type": "error",
                                "data": {
                                    "message": "Missing ride_id or rider_id in ride_accept message"
                                }
                            })
                            continue
                        
                        logger.info(f"Driver {user_id} accepting ride: {ride_id}")
                        
                        # Import here to avoid circular dependency
                        from app.services.matching_service import MatchingService
                        from app.database import get_db
                        from app.config import get_redis_client
                        
                        # Get database session and Redis client
                        db = next(get_db())
                        redis_client = get_redis_client()
                        
                        try:
                            # Create matching service instance
                            matching_service = MatchingService(redis_client, db)
                            
                            # Attempt to match the ride
                            match_result = matching_service.match_ride(
                                ride_id=ride_id,
                                driver_id=user_id,
                                rider_id=rider_id
                            )
                            
                            # Send result back to driver
                            if match_result["status"] == "success":
                                # Send success confirmation to driver
                                await websocket.send_json({
                                    "type": "ride_match_confirmed",
                                    "data": match_result
                                })
                                
                                # Send match notification to rider
                                rider_notification = {
                                    "type": "ride_matched",
                                    "data": {
                                        "ride_id": ride_id,
                                        "driver_id": user_id,
                                        "driver_details": match_result.get("driver_details"),
                                        "vehicle_details": match_result.get("vehicle_details"),
                                        "estimated_arrival_minutes": match_result.get("estimated_arrival_minutes"),
                                        "distance_to_pickup_km": match_result.get("distance_to_pickup_km"),
                                        "matched_at": match_result.get("matched_at")
                                    },
                                    "timestamp": datetime.utcnow().isoformat()
                                }
                                await connection_manager.send_personal_message(rider_notification, rider_id)
                                
                                # Cancel notifications to other drivers
                                broadcast_details = matching_service.get_broadcast_details(ride_id)
                                if broadcast_details:
                                    notified_drivers = broadcast_details.get("notified_drivers", [])
                                    cancellation_message = {
                                        "type": "ride_no_longer_available",
                                        "data": {
                                            "ride_id": ride_id,
                                            "reason": "Ride has been matched to another driver"
                                        },
                                        "timestamp": datetime.utcnow().isoformat()
                                    }
                                    
                                    # Send cancellation to all notified drivers except the matched one
                                    for driver_id in notified_drivers:
                                        if driver_id != user_id:
                                            await connection_manager.send_personal_message(
                                                cancellation_message,
                                                driver_id
                                            )
                                
                                logger.info(f"Ride {ride_id} successfully matched to driver {user_id}")
                            
                            elif match_result["status"] == "already_matched":
                                # Ride already matched to another driver
                                await websocket.send_json({
                                    "type": "ride_match_failed",
                                    "data": {
                                        "ride_id": ride_id,
                                        "reason": "already_matched",
                                        "message": match_result.get("message")
                                    }
                                })
                            
                            elif match_result["status"] == "processing":
                                # Another driver is being processed
                                await websocket.send_json({
                                    "type": "ride_match_processing",
                                    "data": {
                                        "ride_id": ride_id,
                                        "message": match_result.get("message")
                                    }
                                })
                            
                            else:
                                # Other error
                                await websocket.send_json({
                                    "type": "ride_match_failed",
                                    "data": {
                                        "ride_id": ride_id,
                                        "reason": "error",
                                        "message": match_result.get("message")
                                    }
                                })
                        
                        except Exception as e:
                            logger.error(f"Error processing ride acceptance: {e}")
                            await websocket.send_json({
                                "type": "error",
                                "data": {
                                    "message": f"Error processing ride acceptance: {str(e)}"
                                }
                            })
                        
                        finally:
                            db.close()
                    
                    elif message_type == "ride_reject":
                        # Driver rejecting a ride
                        ride_id = message_data.get("ride_id")
                        
                        if not ride_id:
                            await websocket.send_json({
                                "type": "error",
                                "data": {
                                    "message": "Missing ride_id in ride_reject message"
                                }
                            })
                            continue
                        
                        logger.info(f"Driver {user_id} rejecting ride: {ride_id}")
                        
                        # Import here to avoid circular dependency
                        from app.services.matching_service import MatchingService
                        from app.database import get_db
                        from app.config import get_redis_client
                        
                        # Get database session and Redis client
                        db = next(get_db())
                        redis_client = get_redis_client()
                        
                        try:
                            # Create matching service instance
                            matching_service = MatchingService(redis_client, db)
                            
                            # Record the rejection
                            reject_result = matching_service.reject_ride(
                                ride_id=ride_id,
                                driver_id=user_id
                            )
                            
                            # Send result back to driver
                            if reject_result["status"] == "success":
                                await websocket.send_json({
                                    "type": "ride_reject_confirmed",
                                    "data": {
                                        "ride_id": ride_id,
                                        "message": "Ride rejection recorded"
                                    }
                                })
                                
                                logger.info(f"Driver {user_id} rejection of ride {ride_id} recorded")
                            
                            else:
                                await websocket.send_json({
                                    "type": "ride_reject_failed",
                                    "data": {
                                        "ride_id": ride_id,
                                        "message": reject_result.get("message")
                                    }
                                })
                        
                        except Exception as e:
                            logger.error(f"Error processing ride rejection: {e}")
                            await websocket.send_json({
                                "type": "error",
                                "data": {
                                    "message": f"Error processing ride rejection: {str(e)}"
                                }
                            })
                        
                        finally:
                            db.close()
                    
                    else:
                        logger.warning(f"Unknown message type from {user_id}: {message_type}")
                        await websocket.send_json({
                            "type": "error",
                            "data": {
                                "message": f"Unknown message type: {message_type}"
                            }
                        })
                
                except json.JSONDecodeError:
                    logger.error(f"Invalid JSON from {user_id}: {data}")
                    await websocket.send_json({
                        "type": "error",
                        "data": {"message": "Invalid JSON format"}
                    })
        
        except WebSocketDisconnect:
            logger.info(f"WebSocket disconnected normally: user_id={user_id}")
            connection_manager.disconnect(user_id)
        
        except Exception as e:
            logger.error(f"Error in WebSocket connection for {user_id}: {e}")
            connection_manager.disconnect(user_id)
            raise
    
    except WebSocketException:
        # Re-raise WebSocket exceptions
        raise
    
    except Exception as e:
        logger.error(f"Error during WebSocket authentication: {e}")
        raise WebSocketException(
            code=status.WS_1008_POLICY_VIOLATION,
            reason="Authentication failed"
        )


@router.get("/connections")
async def get_connection_stats():
    """
    Get WebSocket connection statistics.
    
    Returns:
        Dictionary with connection counts by type
    """
    return connection_manager.get_connection_count()


@router.get("/connections/{user_id}")
async def get_user_connection(user_id: str):
    """
    Get connection information for a specific user.
    
    Args:
        user_id: User identifier
        
    Returns:
        Connection metadata or 404 if not connected
    """
    info = connection_manager.get_connection_info(user_id)
    if not info:
        return {
            "user_id": user_id,
            "connected": False
        }
    return info
