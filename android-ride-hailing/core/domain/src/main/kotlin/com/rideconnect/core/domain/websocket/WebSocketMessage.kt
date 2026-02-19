package com.rideconnect.core.domain.websocket

import com.rideconnect.core.domain.model.Location

/**
 * Sealed class hierarchy for WebSocket messages.
 * Represents all possible message types exchanged via WebSocket.
 * 
 * Requirements: 17.5, 17.6
 */
sealed class WebSocketMessage {
    
    /**
     * Location update from driver to backend.
     * Sent every 10 seconds while driver is online.
     */
    data class LocationUpdate(
        val latitude: Double,
        val longitude: Double,
        val accuracy: Float,
        val timestamp: Long
    ) : WebSocketMessage()
    
    /**
     * Ride status update from backend to rider/driver.
     * Notifies about ride state changes.
     */
    data class RideStatusUpdate(
        val rideId: String,
        val status: String,
        val timestamp: Long,
        val driverId: String? = null,
        val driverName: String? = null,
        val driverPhone: String? = null,
        val driverRating: Double? = null,
        val vehicleDetails: VehicleInfo? = null
    ) : WebSocketMessage()
    
    /**
     * Ride request notification to driver.
     * Sent when a new ride is matched to the driver.
     */
    data class RideRequest(
        val rideId: String,
        val riderId: String,
        val riderName: String,
        val riderRating: Double,
        val pickupLatitude: Double,
        val pickupLongitude: Double,
        val pickupAddress: String,
        val dropoffLatitude: Double,
        val dropoffLongitude: Double,
        val dropoffAddress: String,
        val estimatedFare: Double,
        val distance: Double,
        val expiresAt: Long // Timestamp when request expires
    ) : WebSocketMessage()
    
    /**
     * Ride accepted notification to rider.
     * Sent when driver accepts the ride request.
     */
    data class RideAccepted(
        val rideId: String,
        val driverId: String,
        val driverName: String,
        val driverPhone: String,
        val driverRating: Double,
        val driverLatitude: Double,
        val driverLongitude: Double,
        val vehicleDetails: VehicleInfo,
        val estimatedArrival: Int // Minutes
    ) : WebSocketMessage()
    
    /**
     * Driver location update to rider.
     * Sent every 10 seconds during active ride.
     */
    data class DriverLocationUpdate(
        val rideId: String,
        val driverId: String,
        val latitude: Double,
        val longitude: Double,
        val heading: Float?, // Direction in degrees
        val timestamp: Long
    ) : WebSocketMessage()
    
    /**
     * Chat message between rider and driver.
     * Sent in real-time during active ride.
     */
    data class ChatMessage(
        val rideId: String,
        val messageId: String,
        val senderId: String,
        val senderName: String,
        val message: String,
        val timestamp: Long
    ) : WebSocketMessage()
    
    /**
     * Heartbeat/ping message to keep connection alive.
     * Sent every 30 seconds.
     */
    data class Ping(
        val timestamp: Long = System.currentTimeMillis()
    ) : WebSocketMessage()
    
    /**
     * Pong response to ping.
     */
    data class Pong(
        val timestamp: Long = System.currentTimeMillis()
    ) : WebSocketMessage()
    
    /**
     * Error message from backend.
     */
    data class Error(
        val code: String,
        val message: String,
        val timestamp: Long = System.currentTimeMillis()
    ) : WebSocketMessage()
    
    /**
     * Authentication message sent after connection.
     */
    data class Authenticate(
        val token: String,
        val userType: String // "rider" or "driver"
    ) : WebSocketMessage()
    
    /**
     * Authentication success response.
     */
    data class AuthenticationSuccess(
        val userId: String,
        val timestamp: Long = System.currentTimeMillis()
    ) : WebSocketMessage()
}

/**
 * Vehicle information for ride requests and acceptance.
 */
data class VehicleInfo(
    val make: String,
    val model: String,
    val color: String,
    val licensePlate: String,
    val vehicleType: String
)

/**
 * Connection state for WebSocket.
 */
enum class ConnectionState {
    DISCONNECTED,
    CONNECTING,
    CONNECTED,
    AUTHENTICATED,
    RECONNECTING,
    ERROR
}
