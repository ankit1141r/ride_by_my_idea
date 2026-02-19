package com.rideconnect.core.domain.websocket

import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.StateFlow

/**
 * Manager for WebSocket connections.
 * Handles real-time bidirectional communication with backend.
 * 
 * Requirements: 17.1, 17.2, 17.3, 17.4, 17.7
 */
interface WebSocketManager {
    
    /**
     * Current connection state.
     */
    val connectionState: StateFlow<ConnectionState>
    
    /**
     * Flow of incoming WebSocket messages.
     */
    val messages: Flow<WebSocketMessage>
    
    /**
     * Connect to WebSocket server with authentication token.
     * 
     * @param token JWT authentication token
     * @param userType "rider" or "driver"
     */
    fun connect(token: String, userType: String)
    
    /**
     * Disconnect from WebSocket server.
     * Cleans up resources and stops reconnection attempts.
     */
    fun disconnect()
    
    /**
     * Send a message through the WebSocket connection.
     * If connection is not established, message will be queued.
     * 
     * @param message Message to send
     */
    fun send(message: WebSocketMessage)
    
    /**
     * Check if WebSocket is currently connected and authenticated.
     */
    fun isConnected(): Boolean
    
    /**
     * Force reconnection attempt.
     * Useful for manual retry after connection loss.
     */
    fun reconnect()
}
