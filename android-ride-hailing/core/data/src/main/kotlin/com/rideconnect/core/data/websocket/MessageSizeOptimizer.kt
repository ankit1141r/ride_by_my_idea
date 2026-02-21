package com.rideconnect.core.data.websocket

import com.google.gson.Gson
import com.rideconnect.core.domain.websocket.WebSocketMessage
import timber.log.Timber

/**
 * Optimizer for WebSocket message sizes
 * Requirements: 23.7
 */
class MessageSizeOptimizer(private val gson: Gson) {
    
    companion object {
        private const val MAX_MESSAGE_SIZE_BYTES = 10 * 1024 // 10 KB
        private const val WARNING_SIZE_BYTES = 8 * 1024 // 8 KB
    }
    
    /**
     * Check if message size is within limits
     * Requirements: 23.7
     */
    fun isWithinSizeLimit(message: WebSocketMessage): Boolean {
        val json = gson.toJson(message)
        val sizeBytes = json.toByteArray().size
        
        return sizeBytes <= MAX_MESSAGE_SIZE_BYTES
    }
    
    /**
     * Get message size in bytes
     */
    fun getMessageSize(message: WebSocketMessage): Int {
        val json = gson.toJson(message)
        return json.toByteArray().size
    }
    
    /**
     * Validate message size and log warning if large
     * Requirements: 23.7
     */
    fun validateMessageSize(message: WebSocketMessage): ValidationResult {
        val sizeBytes = getMessageSize(message)
        
        return when {
            sizeBytes > MAX_MESSAGE_SIZE_BYTES -> {
                Timber.e("Message size ${sizeBytes} bytes exceeds maximum ${MAX_MESSAGE_SIZE_BYTES} bytes")
                ValidationResult.TooLarge(sizeBytes, MAX_MESSAGE_SIZE_BYTES)
            }
            sizeBytes > WARNING_SIZE_BYTES -> {
                Timber.w("Message size ${sizeBytes} bytes is large (warning threshold: ${WARNING_SIZE_BYTES} bytes)")
                ValidationResult.Warning(sizeBytes, WARNING_SIZE_BYTES)
            }
            else -> {
                ValidationResult.Valid(sizeBytes)
            }
        }
    }
    
    /**
     * Optimize message by removing unnecessary fields
     */
    fun optimizeMessage(message: WebSocketMessage): WebSocketMessage {
        return when (message) {
            is WebSocketMessage.LocationUpdate -> {
                // Location updates are already minimal
                message
            }
            is WebSocketMessage.RideStatusUpdate -> {
                // Status updates are already minimal
                message
            }
            is WebSocketMessage.ChatMessage -> {
                // Truncate very long messages
                if (message.message.length > 1000) {
                    message.copy(message = message.message.take(1000) + "...")
                } else {
                    message
                }
            }
            else -> message
        }
    }
    
    /**
     * Compress message data if needed
     */
    fun compressIfNeeded(json: String): String {
        val sizeBytes = json.toByteArray().size
        
        return if (sizeBytes > WARNING_SIZE_BYTES) {
            // Remove whitespace for compression
            json.replace("\\s+".toRegex(), "")
        } else {
            json
        }
    }
    
    /**
     * Get size statistics for monitoring
     */
    fun getSizeStatistics(messages: List<WebSocketMessage>): SizeStatistics {
        val sizes = messages.map { getMessageSize(it) }
        
        return SizeStatistics(
            count = sizes.size,
            totalBytes = sizes.sum(),
            averageBytes = if (sizes.isNotEmpty()) sizes.average() else 0.0,
            maxBytes = sizes.maxOrNull() ?: 0,
            minBytes = sizes.minOrNull() ?: 0,
            oversizedCount = sizes.count { it > MAX_MESSAGE_SIZE_BYTES }
        )
    }
    
    sealed class ValidationResult {
        data class Valid(val sizeBytes: Int) : ValidationResult()
        data class Warning(val sizeBytes: Int, val threshold: Int) : ValidationResult()
        data class TooLarge(val sizeBytes: Int, val maxSize: Int) : ValidationResult()
    }
    
    data class SizeStatistics(
        val count: Int,
        val totalBytes: Int,
        val averageBytes: Double,
        val maxBytes: Int,
        val minBytes: Int,
        val oversizedCount: Int
    ) {
        val averageKB: Double get() = averageBytes / 1024.0
        val totalKB: Double get() = totalBytes / 1024.0
    }
}

/**
 * Extension function to validate message size before sending
 */
fun WebSocketMessage.validateSize(optimizer: MessageSizeOptimizer): Boolean {
    val result = optimizer.validateMessageSize(this)
    return result is MessageSizeOptimizer.ValidationResult.Valid || 
           result is MessageSizeOptimizer.ValidationResult.Warning
}
