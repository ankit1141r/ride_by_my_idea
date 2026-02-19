package com.rideconnect.core.domain.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.rideconnect.core.common.result.Result
import com.rideconnect.core.domain.model.ChatMessage
import com.rideconnect.core.domain.repository.ChatRepository
import com.rideconnect.core.domain.websocket.WebSocketManager
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.launch
import timber.log.Timber
import javax.inject.Inject

/**
 * ViewModel for managing chat functionality.
 * Handles message sending, receiving, and read status tracking.
 * 
 * Requirements: 10.1, 10.2, 10.3, 10.4, 10.7
 */
@HiltViewModel
class ChatViewModel @Inject constructor(
    private val chatRepository: ChatRepository,
    private val webSocketManager: WebSocketManager
) : ViewModel() {
    
    private val _currentRideId = MutableStateFlow<String?>(null)
    
    /**
     * Chat messages for the current ride.
     * Requirements: 10.1, 10.4
     */
    val messages: StateFlow<List<ChatMessage>> = _currentRideId
        .filterNotNull()
        .flatMapLatest { rideId ->
            chatRepository.observeMessages(rideId)
        }
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5000),
            initialValue = emptyList()
        )
    
    /**
     * Unread message count for the current ride.
     * Requirements: 10.3
     */
    val unreadCount: StateFlow<Int> = _currentRideId
        .filterNotNull()
        .flatMapLatest { rideId ->
            chatRepository.getUnreadMessageCount(rideId)
        }
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5000),
            initialValue = 0
        )
    
    private val _sendMessageState = MutableStateFlow<SendMessageState>(SendMessageState.Idle)
    val sendMessageState: StateFlow<SendMessageState> = _sendMessageState.asStateFlow()
    
    private val _error = MutableStateFlow<String?>(null)
    val error: StateFlow<String?> = _error.asStateFlow()
    
    private val _isChatEnabled = MutableStateFlow(true)
    val isChatEnabled: StateFlow<Boolean> = _isChatEnabled.asStateFlow()
    
    /**
     * Set the current ride ID to observe messages for.
     */
    fun setRideId(rideId: String) {
        _currentRideId.value = rideId
    }
    
    /**
     * Archive chat when ride completes.
     * Disables chat functionality after ride ends.
     * Requirements: 10.6
     */
    fun archiveChat() {
        val rideId = _currentRideId.value ?: return
        
        viewModelScope.launch {
            when (val result = chatRepository.archiveChat(rideId)) {
                is Result.Success -> {
                    _isChatEnabled.value = false
                    Timber.d("Chat archived for ride: $rideId")
                }
                is Result.Error -> {
                    Timber.e("Failed to archive chat: ${result.message}")
                }
            }
        }
    }
    
    /**
     * Disable chat functionality (called when ride ends).
     * Requirements: 10.6
     */
    fun disableChat() {
        _isChatEnabled.value = false
    }
    
    /**
     * Send a chat message.
     * Requirements: 10.2
     */
    fun sendMessage(message: String) {
        val rideId = _currentRideId.value
        if (rideId == null) {
            _error.value = "No active ride"
            return
        }
        
        if (message.isBlank()) {
            _error.value = "Message cannot be empty"
            return
        }
        
        if (message.length > 1000) {
            _error.value = "Message must not exceed 1000 characters"
            return
        }
        
        viewModelScope.launch {
            _sendMessageState.value = SendMessageState.Sending
            
            when (val result = chatRepository.sendMessage(rideId, message)) {
                is Result.Success -> {
                    _sendMessageState.value = SendMessageState.Success
                    _error.value = null
                    // Reset to idle after a short delay
                    kotlinx.coroutines.delay(500)
                    _sendMessageState.value = SendMessageState.Idle
                }
                is Result.Error -> {
                    _sendMessageState.value = SendMessageState.Error(result.message)
                    _error.value = result.message
                    Timber.e("Failed to send message: ${result.message}")
                }
            }
        }
    }
    
    /**
     * Mark a specific message as read.
     * Requirements: 10.7
     */
    fun markAsRead(messageId: String) {
        val rideId = _currentRideId.value ?: return
        
        viewModelScope.launch {
            when (val result = chatRepository.markAsRead(rideId, messageId)) {
                is Result.Success -> {
                    Timber.d("Message marked as read: $messageId")
                }
                is Result.Error -> {
                    Timber.e("Failed to mark message as read: ${result.message}")
                }
            }
        }
    }
    
    /**
     * Mark all messages in the current ride as read.
     * Requirements: 10.7
     */
    fun markAllAsRead() {
        val rideId = _currentRideId.value ?: return
        
        viewModelScope.launch {
            when (val result = chatRepository.markAllAsRead(rideId)) {
                is Result.Success -> {
                    Timber.d("All messages marked as read for ride: $rideId")
                }
                is Result.Error -> {
                    Timber.e("Failed to mark all messages as read: ${result.message}")
                }
            }
        }
    }
    
    /**
     * Clear error message.
     */
    fun clearError() {
        _error.value = null
    }
    
    /**
     * Listen for incoming WebSocket messages.
     * This should be called when the chat screen is active.
     */
    fun startListeningForMessages() {
        viewModelScope.launch {
            webSocketManager.messages.collect { wsMessage ->
                if (wsMessage is com.rideconnect.core.domain.websocket.WebSocketMessage.ChatMessage) {
                    // Message will be automatically stored in database by WebSocketManager
                    // and will appear in the messages Flow
                    Timber.d("Received chat message: ${wsMessage.messageId}")
                }
            }
        }
    }
}

/**
 * State for message sending operation.
 */
sealed class SendMessageState {
    object Idle : SendMessageState()
    object Sending : SendMessageState()
    object Success : SendMessageState()
    data class Error(val message: String) : SendMessageState()
}
