"""
Tests for WebSocket connection management.

Tests cover:
- WebSocket connection with JWT authentication
- Connection lifecycle (connect, disconnect, reconnect)
- Connection pool management
- Message sending and broadcasting
- Connection statistics
"""
import pytest
from fastapi.testclient import TestClient
from uuid import uuid4
from app.main import app
from app.services.websocket_service import ConnectionManager
from app.utils.jwt import create_access_token


@pytest.fixture
def connection_manager():
    """Create a fresh connection manager for each test."""
    return ConnectionManager()


@pytest.fixture
def rider_token():
    """Create a JWT token for a rider."""
    user_id = str(uuid4())
    token = create_access_token(user_id, "rider", True)
    return token, user_id


@pytest.fixture
def driver_token():
    """Create a JWT token for a driver."""
    user_id = str(uuid4())
    token = create_access_token(user_id, "driver", True)
    return token, user_id


def test_websocket_connection_with_valid_token(rider_token):
    """Test WebSocket connection with valid JWT token."""
    token, user_id = rider_token
    client = TestClient(app)
    
    with client.websocket_connect(f"/ws?token={token}") as websocket:
        # Should receive connection confirmation
        data = websocket.receive_json()
        assert data["type"] == "connection_established"
        assert data["data"]["user_id"] == user_id
        assert data["data"]["user_type"] == "rider"


def test_websocket_connection_without_token():
    """Test WebSocket connection fails without token."""
    client = TestClient(app)
    
    with pytest.raises(Exception):
        with client.websocket_connect("/ws"):
            pass


def test_websocket_connection_with_invalid_token():
    """Test WebSocket connection fails with invalid token."""
    client = TestClient(app)
    
    with pytest.raises(Exception):
        with client.websocket_connect("/ws?token=invalid_token"):
            pass


def test_websocket_ping_pong(rider_token):
    """Test ping-pong message exchange."""
    token, user_id = rider_token
    client = TestClient(app)
    
    with client.websocket_connect(f"/ws?token={token}") as websocket:
        # Receive connection confirmation
        websocket.receive_json()
        
        # Send ping
        websocket.send_json({
            "type": "ping",
            "data": {"timestamp": "2024-01-01T00:00:00Z"}
        })
        
        # Should receive pong
        response = websocket.receive_json()
        assert response["type"] == "pong"
        assert response["data"]["timestamp"] == "2024-01-01T00:00:00Z"


def test_connection_manager_connect(connection_manager):
    """Test connection manager connect functionality."""
    from unittest.mock import AsyncMock, MagicMock
    
    # Create mock websocket
    websocket = AsyncMock()
    websocket.accept = AsyncMock()
    
    user_id = str(uuid4())
    
    # Connect user
    import asyncio
    asyncio.run(connection_manager.connect(websocket, user_id, "rider"))
    
    # Verify connection registered
    assert connection_manager.is_connected(user_id)
    assert user_id in connection_manager.rider_connections
    assert user_id not in connection_manager.driver_connections


def test_connection_manager_disconnect(connection_manager):
    """Test connection manager disconnect functionality."""
    from unittest.mock import AsyncMock
    
    # Create mock websocket
    websocket = AsyncMock()
    websocket.accept = AsyncMock()
    
    user_id = str(uuid4())
    
    # Connect and then disconnect
    import asyncio
    asyncio.run(connection_manager.connect(websocket, user_id, "driver"))
    assert connection_manager.is_connected(user_id)
    
    connection_manager.disconnect(user_id)
    assert not connection_manager.is_connected(user_id)
    assert user_id not in connection_manager.driver_connections


def test_connection_manager_reconnect(connection_manager):
    """Test that reconnecting closes old connection."""
    from unittest.mock import AsyncMock
    
    # Create mock websockets
    old_websocket = AsyncMock()
    old_websocket.accept = AsyncMock()
    old_websocket.close = AsyncMock()
    
    new_websocket = AsyncMock()
    new_websocket.accept = AsyncMock()
    
    user_id = str(uuid4())
    
    import asyncio
    
    # Connect first time
    asyncio.run(connection_manager.connect(old_websocket, user_id, "rider"))
    assert connection_manager.is_connected(user_id)
    
    # Reconnect with new websocket
    asyncio.run(connection_manager.connect(new_websocket, user_id, "rider"))
    
    # Old websocket should be closed
    old_websocket.close.assert_called_once()
    
    # New connection should be active
    assert connection_manager.is_connected(user_id)
    assert connection_manager.active_connections[user_id] == new_websocket


def test_connection_manager_send_personal_message(connection_manager):
    """Test sending message to specific user."""
    from unittest.mock import AsyncMock
    
    # Create mock websocket
    websocket = AsyncMock()
    websocket.accept = AsyncMock()
    websocket.send_json = AsyncMock()
    
    user_id = str(uuid4())
    
    import asyncio
    
    # Connect user
    asyncio.run(connection_manager.connect(websocket, user_id, "rider"))
    
    # Send message
    message = {"type": "test", "data": {"content": "Hello"}}
    result = asyncio.run(connection_manager.send_personal_message(message, user_id))
    
    assert result is True
    websocket.send_json.assert_called_once_with(message)


def test_connection_manager_send_to_disconnected_user(connection_manager):
    """Test sending message to disconnected user fails gracefully."""
    import asyncio
    
    user_id = str(uuid4())
    message = {"type": "test", "data": {"content": "Hello"}}
    
    # Try to send to non-existent user
    result = asyncio.run(connection_manager.send_personal_message(message, user_id))
    
    assert result is False


def test_connection_manager_broadcast_to_drivers(connection_manager):
    """Test broadcasting message to all drivers."""
    from unittest.mock import AsyncMock
    
    import asyncio
    
    # Create multiple driver connections
    driver_ids = [str(uuid4()) for _ in range(3)]
    
    for driver_id in driver_ids:
        websocket = AsyncMock()
        websocket.accept = AsyncMock()
        websocket.send_json = AsyncMock()
        asyncio.run(connection_manager.connect(websocket, driver_id, "driver"))
    
    # Broadcast message
    message = {"type": "ride_request", "data": {"ride_id": "123"}}
    count = asyncio.run(connection_manager.broadcast_to_drivers(message))
    
    assert count == 3


def test_connection_manager_broadcast_to_specific_drivers(connection_manager):
    """Test broadcasting message to specific drivers only."""
    from unittest.mock import AsyncMock
    
    import asyncio
    
    # Create multiple driver connections
    driver_ids = [str(uuid4()) for _ in range(5)]
    
    for driver_id in driver_ids:
        websocket = AsyncMock()
        websocket.accept = AsyncMock()
        websocket.send_json = AsyncMock()
        asyncio.run(connection_manager.connect(websocket, driver_id, "driver"))
    
    # Broadcast to only 2 specific drivers
    target_drivers = set(driver_ids[:2])
    message = {"type": "ride_request", "data": {"ride_id": "123"}}
    count = asyncio.run(connection_manager.broadcast_to_drivers(message, target_drivers))
    
    assert count == 2


def test_connection_manager_get_connection_count(connection_manager):
    """Test getting connection statistics."""
    from unittest.mock import AsyncMock
    
    import asyncio
    
    # Create mixed connections
    for i in range(3):
        websocket = AsyncMock()
        websocket.accept = AsyncMock()
        asyncio.run(connection_manager.connect(websocket, f"driver_{i}", "driver"))
    
    for i in range(2):
        websocket = AsyncMock()
        websocket.accept = AsyncMock()
        asyncio.run(connection_manager.connect(websocket, f"rider_{i}", "rider"))
    
    stats = connection_manager.get_connection_count()
    
    assert stats["total"] == 5
    assert stats["drivers"] == 3
    assert stats["riders"] == 2


def test_connection_manager_get_connection_info(connection_manager):
    """Test getting connection metadata for a user."""
    from unittest.mock import AsyncMock
    
    import asyncio
    
    websocket = AsyncMock()
    websocket.accept = AsyncMock()
    user_id = str(uuid4())
    
    asyncio.run(connection_manager.connect(websocket, user_id, "rider"))
    
    info = connection_manager.get_connection_info(user_id)
    
    assert info is not None
    assert info["user_id"] == user_id
    assert info["user_type"] == "rider"
    assert info["connected"] is True
    assert "connected_at" in info
    assert "last_activity" in info


def test_websocket_connection_stats_endpoint(rider_token):
    """Test WebSocket connection statistics endpoint."""
    token, user_id = rider_token
    client = TestClient(app)
    
    # Connect a WebSocket
    with client.websocket_connect(f"/ws?token={token}"):
        # Query stats endpoint
        response = client.get("/ws/connections")
        assert response.status_code == 200
        
        data = response.json()
        assert "total" in data
        assert "drivers" in data
        assert "riders" in data


def test_websocket_user_connection_info_endpoint(rider_token):
    """Test getting user connection info via endpoint."""
    token, user_id = rider_token
    client = TestClient(app)
    
    # Connect a WebSocket
    with client.websocket_connect(f"/ws?token={token}"):
        # Query user connection info
        response = client.get(f"/ws/connections/{user_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["user_id"] == user_id
        assert data["connected"] is True
