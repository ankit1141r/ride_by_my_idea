"""
WebSocket Service for real-time communication.

Manages WebSocket connections, authentication, and message broadcasting.
"""
from typing import Dict, Set, Optional
from fastapi import WebSocket
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)


class ConnectionManager:
    """
    Manages WebSocket connections for riders and drivers.
    
    Maintains separate connection pools for riders and drivers,
    handles authentication, and provides methods for broadcasting
    messages to specific users or groups.
    """
    
    def __init__(self):
        # Active connections: {user_id: WebSocket}
        self.active_connections: Dict[str, WebSocket] = {}
        
        # User type mapping: {user_id: 'rider' | 'driver'}
        self.user_types: Dict[str, str] = {}
        
        # Connection metadata: {user_id: {connected_at, last_activity}}
        self.connection_metadata: Dict[str, Dict] = {}
        
        # Driver connections set for quick filtering
        self.driver_connections: Set[str] = set()
        
        # Rider connections set for quick filtering
        self.rider_connections: Set[str] = set()
    
    async def connect(
        self,
        websocket: WebSocket,
        user_id: str,
        user_type: str
    ) -> None:
        """
        Accept and register a new WebSocket connection.
        
        Args:
            websocket: WebSocket connection instance
            user_id: Unique user identifier
            user_type: Type of user ('rider' or 'driver')
        """
        await websocket.accept()
        
        # If user already has a connection, close the old one
        if user_id in self.active_connections:
            try:
                old_websocket = self.active_connections[user_id]
                await old_websocket.close(code=1000, reason="New connection established")
            except Exception as e:
                logger.warning(f"Error closing old connection for user {user_id}: {e}")
        
        # Register new connection
        self.active_connections[user_id] = websocket
        self.user_types[user_id] = user_type
        self.connection_metadata[user_id] = {
            "connected_at": datetime.utcnow().isoformat(),
            "last_activity": datetime.utcnow().isoformat()
        }
        
        # Add to appropriate connection set
        if user_type == "driver":
            self.driver_connections.add(user_id)
        elif user_type == "rider":
            self.rider_connections.add(user_id)
        
        logger.info(f"WebSocket connected: user_id={user_id}, type={user_type}")
    
    def disconnect(self, user_id: str) -> None:
        """
        Remove a WebSocket connection.
        
        Args:
            user_id: Unique user identifier
        """
        if user_id in self.active_connections:
            del self.active_connections[user_id]
        
        if user_id in self.user_types:
            user_type = self.user_types[user_id]
            del self.user_types[user_id]
            
            # Remove from appropriate connection set
            if user_type == "driver":
                self.driver_connections.discard(user_id)
            elif user_type == "rider":
                self.rider_connections.discard(user_id)
        
        if user_id in self.connection_metadata:
            del self.connection_metadata[user_id]
        
        logger.info(f"WebSocket disconnected: user_id={user_id}")
    
    def is_connected(self, user_id: str) -> bool:
        """
        Check if a user is currently connected.
        
        Args:
            user_id: Unique user identifier
            
        Returns:
            True if user has an active connection, False otherwise
        """
        return user_id in self.active_connections
    
    async def send_personal_message(
        self,
        message: dict,
        user_id: str
    ) -> bool:
        """
        Send a message to a specific user.
        
        Args:
            message: Message data as dictionary
            user_id: Target user identifier
            
        Returns:
            True if message sent successfully, False otherwise
        """
        if user_id not in self.active_connections:
            logger.warning(f"Cannot send message: user {user_id} not connected")
            return False
        
        try:
            websocket = self.active_connections[user_id]
            await websocket.send_json(message)
            
            # Update last activity
            if user_id in self.connection_metadata:
                self.connection_metadata[user_id]["last_activity"] = datetime.utcnow().isoformat()
            
            logger.debug(f"Message sent to user {user_id}: {message.get('type', 'unknown')}")
            return True
        except Exception as e:
            logger.error(f"Error sending message to user {user_id}: {e}")
            # Connection might be broken, disconnect it
            self.disconnect(user_id)
            return False
    
    async def broadcast_to_drivers(
        self,
        message: dict,
        driver_ids: Optional[Set[str]] = None
    ) -> int:
        """
        Broadcast a message to all drivers or specific drivers.
        
        Args:
            message: Message data as dictionary
            driver_ids: Optional set of specific driver IDs to target.
                       If None, broadcasts to all connected drivers.
            
        Returns:
            Number of drivers who received the message
        """
        target_drivers = driver_ids if driver_ids else self.driver_connections
        sent_count = 0
        
        for driver_id in target_drivers:
            if await self.send_personal_message(message, driver_id):
                sent_count += 1
        
        logger.info(f"Broadcast to {sent_count} drivers: {message.get('type', 'unknown')}")
        return sent_count
    
    async def broadcast_to_riders(
        self,
        message: dict,
        rider_ids: Optional[Set[str]] = None
    ) -> int:
        """
        Broadcast a message to all riders or specific riders.
        
        Args:
            message: Message data as dictionary
            rider_ids: Optional set of specific rider IDs to target.
                      If None, broadcasts to all connected riders.
            
        Returns:
            Number of riders who received the message
        """
        target_riders = rider_ids if rider_ids else self.rider_connections
        sent_count = 0
        
        for rider_id in target_riders:
            if await self.send_personal_message(message, rider_id):
                sent_count += 1
        
        logger.info(f"Broadcast to {sent_count} riders: {message.get('type', 'unknown')}")
        return sent_count
    
    def get_connection_count(self) -> Dict[str, int]:
        """
        Get count of active connections by type.
        
        Returns:
            Dictionary with connection counts
        """
        return {
            "total": len(self.active_connections),
            "drivers": len(self.driver_connections),
            "riders": len(self.rider_connections)
        }
    
    def get_connection_info(self, user_id: str) -> Optional[Dict]:
        """
        Get connection metadata for a specific user.
        
        Args:
            user_id: Unique user identifier
            
        Returns:
            Connection metadata dictionary or None if not connected
        """
        if user_id not in self.connection_metadata:
            return None
        
        return {
            "user_id": user_id,
            "user_type": self.user_types.get(user_id),
            "connected": True,
            **self.connection_metadata[user_id]
        }


# Global connection manager instance
connection_manager = ConnectionManager()
