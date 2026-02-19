package com.rideconnect.core.domain.model

/**
 * Chat message data model.
 * Requirements: 10.1, 10.4, 10.5, 10.7
 */
data class ChatMessage(
    val id: String,
    val rideId: String,
    val senderId: String,
    val message: String,
    val timestamp: Long,
    val status: MessageStatus
)

/**
 * Message delivery status.
 * Requirements: 10.7
 */
enum class MessageStatus {
    SENT,
    DELIVERED,
    READ;
    
    companion object {
        fun fromString(value: String): MessageStatus {
            return when (value.uppercase()) {
                "SENT" -> SENT
                "DELIVERED" -> DELIVERED
                "READ" -> READ
                else -> SENT
            }
        }
    }
}

/**
 * Request to send a chat message.
 * Requirements: 10.1, 10.2
 */
data class SendMessageRequest(
    val rideId: String,
    val message: String
) {
    init {
        require(message.isNotBlank()) { "Message cannot be blank" }
        require(message.length <= 1000) { "Message must not exceed 1000 characters" }
    }
}
