package com.rideconnect.core.network.config

/**
 * WebSocket configuration
 * Requirements: 24.4
 */
object WebSocketConfig {
    
    /**
     * Get WebSocket URL based on build type
     * Production uses WSS (secure WebSocket), development uses WS
     * Requirements: 24.4
     */
    fun getWebSocketUrl(isDebug: Boolean): String {
        return if (isDebug) {
            // Development: Use unsecure WebSocket for local testing
            "ws://10.0.2.2:8000/ws" // Android emulator localhost
        } else {
            // Production: Use secure WebSocket (WSS)
            "wss://api.rideconnect.com/ws"
        }
    }
    
    /**
     * Get WebSocket URL for custom host
     */
    fun getWebSocketUrl(host: String, useSecure: Boolean = true): String {
        val protocol = if (useSecure) "wss" else "ws"
        return "$protocol://$host/ws"
    }
    
    /**
     * Validate WebSocket URL uses secure protocol in production
     */
    fun isSecureWebSocket(url: String): Boolean {
        return url.startsWith("wss://")
    }
    
    /**
     * Ensure WebSocket URL is secure for production builds
     */
    fun enforceSecureWebSocket(url: String, isDebug: Boolean): String {
        if (!isDebug && !isSecureWebSocket(url)) {
            throw SecurityException(
                "Insecure WebSocket connection not allowed in production. " +
                "Use WSS protocol instead of WS."
            )
        }
        return url
    }
}
