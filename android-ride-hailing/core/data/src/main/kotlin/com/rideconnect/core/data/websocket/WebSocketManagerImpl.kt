package com.rideconnect.core.data.websocket

import com.google.gson.Gson
import com.rideconnect.core.domain.websocket.ConnectionState
import com.rideconnect.core.domain.websocket.WebSocketManager
import com.rideconnect.core.domain.websocket.WebSocketMessage
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*
import okhttp3.*
import timber.log.Timber
import java.util.concurrent.TimeUnit
import javax.inject.Inject
import javax.inject.Singleton

/**
 * Implementation of WebSocketManager using OkHttp.
 * Handles WebSocket connection, reconnection, and message handling.
 * 
 * Requirements: 17.1, 17.2, 17.3, 17.4, 17.7
 */
@Singleton
class WebSocketManagerImpl @Inject constructor(
    private val okHttpClient: OkHttpClient,
    private val gson: Gson
) : WebSocketManager {
    
    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.IO)
    
    private val _connectionState = MutableStateFlow(ConnectionState.DISCONNECTED)
    override val connectionState: StateFlow<ConnectionState> = _connectionState.asStateFlow()
    
    private val _messages = MutableSharedFlow<WebSocketMessage>(
        replay = 0,
        extraBufferCapacity = 100
    )
    override val messages: Flow<WebSocketMessage> = _messages.asSharedFlow()
    
    private var webSocket: WebSocket? = null
    private var reconnectJob: Job? = null
    private var pingJob: Job? = null
    
    private val messageQueue = mutableListOf<WebSocketMessage>()
    private var reconnectAttempts = 0
    private val maxReconnectAttempts = 10
    
    private var authToken: String? = null
    private var userType: String? = null
    private var wsUrl: String = "ws://localhost:8000/ws" // Default, should be configured
    
    companion object {
        private const val PING_INTERVAL_MS = 30_000L // 30 seconds
        private const val INITIAL_RECONNECT_DELAY_MS = 1000L // 1 second
        private const val MAX_RECONNECT_DELAY_MS = 30_000L // 30 seconds
    }
    
    override fun connect(token: String, userType: String) {
        this.authToken = token
        this.userType = userType
        
        if (_connectionState.value == ConnectionState.CONNECTED || 
            _connectionState.value == ConnectionState.CONNECTING) {
            Timber.d("Already connected or connecting")
            return
        }
        
        performConnect()
    }
    
    private fun performConnect() {
        _connectionState.value = ConnectionState.CONNECTING
        reconnectJob?.cancel()
        
        try {
            val request = Request.Builder()
                .url(wsUrl)
                .build()
            
            webSocket = okHttpClient.newWebSocket(request, webSocketListener)
            Timber.d("WebSocket connection initiated")
        } catch (e: Exception) {
            Timber.e(e, "Failed to initiate WebSocket connection")
            _connectionState.value = ConnectionState.ERROR
            scheduleReconnect()
        }
    }
    
    override fun disconnect() {
        Timber.d("Disconnecting WebSocket")
        reconnectJob?.cancel()
        pingJob?.cancel()
        webSocket?.close(1000, "Client disconnect")
        webSocket = null
        _connectionState.value = ConnectionState.DISCONNECTED
        reconnectAttempts = 0
        messageQueue.clear()
    }
    
    override fun send(message: WebSocketMessage) {
        if (_connectionState.value != ConnectionState.AUTHENTICATED) {
            Timber.w("WebSocket not authenticated, queueing message")
            messageQueue.add(message)
            return
        }
        
        try {
            val json = serializeMessage(message)
            val success = webSocket?.send(json) ?: false
            
            if (success) {
                Timber.d("Message sent: ${message::class.simpleName}")
            } else {
                Timber.w("Failed to send message, queueing")
                messageQueue.add(message)
            }
        } catch (e: Exception) {
            Timber.e(e, "Error sending message")
            messageQueue.add(message)
        }
    }
    
    override fun isConnected(): Boolean {
        return _connectionState.value == ConnectionState.AUTHENTICATED
    }
    
    override fun reconnect() {
        Timber.d("Manual reconnect requested")
        disconnect()
        authToken?.let { token ->
            userType?.let { type ->
                connect(token, type)
            }
        }
    }
    
    private val webSocketListener = object : WebSocketListener() {
        
        override fun onOpen(webSocket: WebSocket, response: Response) {
            Timber.d("WebSocket opened")
            _connectionState.value = ConnectionState.CONNECTED
            reconnectAttempts = 0
            
            // Send authentication message
            authToken?.let { token ->
                userType?.let { type ->
                    val authMessage = WebSocketMessage.Authenticate(token, type)
                    send(authMessage)
                }
            }
            
            // Start ping/pong heartbeat
            startPingJob()
        }
        
        override fun onMessage(webSocket: WebSocket, text: String) {
            Timber.d("WebSocket message received: ${text.take(100)}")
            
            try {
                val message = deserializeMessage(text)
                
                // Handle authentication success
                if (message is WebSocketMessage.AuthenticationSuccess) {
                    _connectionState.value = ConnectionState.AUTHENTICATED
                    Timber.d("WebSocket authenticated")
                    
                    // Send queued messages
                    flushMessageQueue()
                }
                
                // Emit message to flow
                scope.launch {
                    _messages.emit(message)
                }
            } catch (e: Exception) {
                Timber.e(e, "Error parsing WebSocket message")
            }
        }
        
        override fun onClosing(webSocket: WebSocket, code: Int, reason: String) {
            Timber.d("WebSocket closing: $code - $reason")
            webSocket.close(1000, null)
        }
        
        override fun onClosed(webSocket: WebSocket, code: Int, reason: String) {
            Timber.d("WebSocket closed: $code - $reason")
            pingJob?.cancel()
            
            if (_connectionState.value != ConnectionState.DISCONNECTED) {
                _connectionState.value = ConnectionState.DISCONNECTED
                scheduleReconnect()
            }
        }
        
        override fun onFailure(webSocket: WebSocket, t: Throwable, response: Response?) {
            Timber.e(t, "WebSocket failure: ${response?.message}")
            _connectionState.value = ConnectionState.ERROR
            pingJob?.cancel()
            scheduleReconnect()
        }
    }
    
    private fun scheduleReconnect() {
        if (reconnectAttempts >= maxReconnectAttempts) {
            Timber.w("Max reconnect attempts reached")
            _connectionState.value = ConnectionState.ERROR
            return
        }
        
        _connectionState.value = ConnectionState.RECONNECTING
        
        // Exponential backoff: 1s, 2s, 4s, 8s, 16s, 30s (max)
        val delay = minOf(
            INITIAL_RECONNECT_DELAY_MS * (1 shl reconnectAttempts),
            MAX_RECONNECT_DELAY_MS
        )
        
        reconnectAttempts++
        Timber.d("Scheduling reconnect attempt $reconnectAttempts in ${delay}ms")
        
        reconnectJob = scope.launch {
            delay(delay)
            performConnect()
        }
    }
    
    private fun startPingJob() {
        pingJob?.cancel()
        pingJob = scope.launch {
            while (isActive && _connectionState.value == ConnectionState.AUTHENTICATED) {
                delay(PING_INTERVAL_MS)
                send(WebSocketMessage.Ping())
            }
        }
    }
    
    private fun flushMessageQueue() {
        if (messageQueue.isEmpty()) return
        
        Timber.d("Flushing ${messageQueue.size} queued messages")
        val messages = messageQueue.toList()
        messageQueue.clear()
        
        messages.forEach { message ->
            send(message)
        }
    }
    
    /**
     * Serialize WebSocket message to JSON.
     */
    private fun serializeMessage(message: WebSocketMessage): String {
        val envelope = MessageEnvelope(
            type = message::class.simpleName ?: "Unknown",
            data = message
        )
        return gson.toJson(envelope)
    }
    
    /**
     * Deserialize JSON to WebSocket message.
     */
    private fun deserializeMessage(json: String): WebSocketMessage {
        val envelope = gson.fromJson(json, MessageEnvelope::class.java)
        
        return when (envelope.type) {
            "LocationUpdate" -> gson.fromJson(gson.toJson(envelope.data), WebSocketMessage.LocationUpdate::class.java)
            "RideStatusUpdate" -> gson.fromJson(gson.toJson(envelope.data), WebSocketMessage.RideStatusUpdate::class.java)
            "RideRequest" -> gson.fromJson(gson.toJson(envelope.data), WebSocketMessage.RideRequest::class.java)
            "RideAccepted" -> gson.fromJson(gson.toJson(envelope.data), WebSocketMessage.RideAccepted::class.java)
            "DriverLocationUpdate" -> gson.fromJson(gson.toJson(envelope.data), WebSocketMessage.DriverLocationUpdate::class.java)
            "ChatMessage" -> gson.fromJson(gson.toJson(envelope.data), WebSocketMessage.ChatMessage::class.java)
            "Ping" -> gson.fromJson(gson.toJson(envelope.data), WebSocketMessage.Ping::class.java)
            "Pong" -> gson.fromJson(gson.toJson(envelope.data), WebSocketMessage.Pong::class.java)
            "Error" -> gson.fromJson(gson.toJson(envelope.data), WebSocketMessage.Error::class.java)
            "AuthenticationSuccess" -> gson.fromJson(gson.toJson(envelope.data), WebSocketMessage.AuthenticationSuccess::class.java)
            else -> {
                Timber.w("Unknown message type: ${envelope.type}")
                WebSocketMessage.Error("UNKNOWN_TYPE", "Unknown message type: ${envelope.type}")
            }
        }
    }
    
    /**
     * Message envelope for JSON serialization.
     */
    private data class MessageEnvelope(
        val type: String,
        val data: Any
    )
}
