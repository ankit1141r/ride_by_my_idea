package com.rideconnect.core.domain.repository

import com.rideconnect.core.common.result.Result
import com.rideconnect.core.domain.model.ChatMessage
import kotlinx.coroutines.flow.Flow

/**
 * Repository interface for chat operations.
 * Handles sending messages, observing messages, and marking messages as read.
 * 
 * Requirements: 10.2, 10.5, 10.6, 10.8
 */
interface ChatRepository {
    /**
     * Send a chat message via WebSocket.
     * Falls back to REST API if WebSocket is unavailable.
     * Queues message for delivery when offline.
     * 
     * Requirements: 10.2, 10.8
     */
    suspend fun sendMessage(rideId: String, message: String): Result<ChatMessage>
    
    /**
     * Observe chat messages for a specific ride.
     * Returns a Flow that emits updated message lists.
     * 
     * Requirements: 10.5
     */
    fun observeMessages(rideId: String): Flow<List<ChatMessage>>
    
    /**
     * Mark a specific message as read.
     * Updates local database and notifies backend via WebSocket.
     * 
     * Requirements: 10.7
     */
    suspend fun markAsRead(rideId: String, messageId: String): Result<Unit>
    
    /**
     * Mark all messages in a ride as read.
     * Updates local database and notifies backend via WebSocket.
     * 
     * Requirements: 10.7
     */
    suspend fun markAllAsRead(rideId: String): Result<Unit>
    
    /**
     * Get unread message count for a specific ride.
     * 
     * Requirements: 10.3
     */
    fun getUnreadMessageCount(rideId: String): Flow<Int>
    
    /**
     * Archive chat messages when ride completes.
     * Disables chat functionality after ride ends.
     * 
     * Requirements: 10.6
     */
    suspend fun archiveChat(rideId: String): Result<Unit>
    
    /**
     * Sync pending messages when connection is restored.
     * 
     * Requirements: 10.8
     */
    suspend fun syncPendingMessages(): Result<Unit>
}
