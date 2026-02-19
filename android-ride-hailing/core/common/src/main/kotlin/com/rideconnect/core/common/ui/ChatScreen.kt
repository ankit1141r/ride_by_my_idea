package com.rideconnect.core.common.ui

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.lazy.rememberLazyListState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.automirrored.filled.Send
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import com.rideconnect.core.domain.model.ChatMessage
import com.rideconnect.core.domain.model.MessageStatus
import com.rideconnect.core.domain.viewmodel.ChatViewModel
import com.rideconnect.core.domain.viewmodel.SendMessageState
import java.text.SimpleDateFormat
import java.util.*

/**
 * Chat screen for rider-driver communication.
 * Displays message list and input field.
 * 
 * Requirements: 10.1, 10.2, 10.3, 10.4, 10.7
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ChatScreen(
    rideId: String,
    currentUserId: String,
    otherUserName: String,
    onBackClick: () -> Unit,
    viewModel: ChatViewModel = hiltViewModel()
) {
    val messages by viewModel.messages.collectAsState()
    val unreadCount by viewModel.unreadCount.collectAsState()
    val sendMessageState by viewModel.sendMessageState.collectAsState()
    val error by viewModel.error.collectAsState()
    val isChatEnabled by viewModel.isChatEnabled.collectAsState()
    
    var messageText by remember { mutableStateOf("") }
    val listState = rememberLazyListState()
    
    // Set ride ID when screen is first composed
    LaunchedEffect(rideId) {
        viewModel.setRideId(rideId)
        viewModel.startListeningForMessages()
    }
    
    // Auto-scroll to bottom when new messages arrive
    LaunchedEffect(messages.size) {
        if (messages.isNotEmpty()) {
            listState.animateScrollToItem(messages.size - 1)
        }
    }
    
    // Mark messages as read when screen is visible
    LaunchedEffect(messages) {
        if (messages.isNotEmpty()) {
            viewModel.markAllAsRead()
        }
    }
    
    Scaffold(
        topBar = {
            TopAppBar(
                title = {
                    Column {
                        Text(text = otherUserName)
                        if (unreadCount > 0) {
                            Text(
                                text = "$unreadCount unread messages",
                                style = MaterialTheme.typography.bodySmall,
                                color = MaterialTheme.colorScheme.onSurfaceVariant
                            )
                        }
                    }
                },
                navigationIcon = {
                    IconButton(onClick = onBackClick) {
                        Icon(
                            imageVector = Icons.AutoMirrored.Filled.ArrowBack,
                            contentDescription = "Back"
                        )
                    }
                }
            )
        },
        bottomBar = {
            if (isChatEnabled) {
                ChatInputBar(
                    messageText = messageText,
                    onMessageTextChange = { messageText = it },
                    onSendClick = {
                        if (messageText.isNotBlank()) {
                            viewModel.sendMessage(messageText)
                            messageText = ""
                        }
                    },
                    isSending = sendMessageState is SendMessageState.Sending,
                    enabled = messageText.isNotBlank() && messageText.length <= 1000
                )
            } else {
                Surface(
                    modifier = Modifier.fillMaxWidth(),
                    tonalElevation = 3.dp
                ) {
                    Box(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(16.dp),
                        contentAlignment = Alignment.Center
                    ) {
                        Text(
                            text = "Chat is disabled. Ride has ended.",
                            style = MaterialTheme.typography.bodyMedium,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }
                }
            }
        }
    ) { paddingValues ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
        ) {
            // Error message
            error?.let { errorMessage ->
                Surface(
                    modifier = Modifier.fillMaxWidth(),
                    color = MaterialTheme.colorScheme.errorContainer
                ) {
                    Row(
                        modifier = Modifier.padding(16.dp),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Text(
                            text = errorMessage,
                            color = MaterialTheme.colorScheme.onErrorContainer,
                            style = MaterialTheme.typography.bodyMedium,
                            modifier = Modifier.weight(1f)
                        )
                        TextButton(onClick = { viewModel.clearError() }) {
                            Text("Dismiss")
                        }
                    }
                }
            }
            
            // Messages list
            if (messages.isEmpty()) {
                Box(
                    modifier = Modifier.fillMaxSize(),
                    contentAlignment = Alignment.Center
                ) {
                    Text(
                        text = "No messages yet\nStart a conversation!",
                        style = MaterialTheme.typography.bodyLarge,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                        textAlign = TextAlign.Center
                    )
                }
            } else {
                LazyColumn(
                    state = listState,
                    modifier = Modifier
                        .fillMaxSize()
                        .weight(1f),
                    contentPadding = PaddingValues(16.dp),
                    verticalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    items(messages, key = { it.id }) { message ->
                        ChatMessageItem(
                            message = message,
                            isOwnMessage = message.senderId == currentUserId
                        )
                    }
                }
            }
        }
    }
}

/**
 * Chat input bar with text field and send button.
 */
@Composable
fun ChatInputBar(
    messageText: String,
    onMessageTextChange: (String) -> Unit,
    onSendClick: () -> Unit,
    isSending: Boolean,
    enabled: Boolean
) {
    Surface(
        modifier = Modifier.fillMaxWidth(),
        tonalElevation = 3.dp
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(8.dp),
            verticalAlignment = Alignment.Bottom
        ) {
            OutlinedTextField(
                value = messageText,
                onValueChange = onMessageTextChange,
                modifier = Modifier
                    .weight(1f)
                    .padding(end = 8.dp),
                placeholder = { Text("Type a message...") },
                maxLines = 4,
                enabled = !isSending,
                supportingText = {
                    Text(
                        text = "${messageText.length}/1000",
                        style = MaterialTheme.typography.bodySmall,
                        color = if (messageText.length > 1000) {
                            MaterialTheme.colorScheme.error
                        } else {
                            MaterialTheme.colorScheme.onSurfaceVariant
                        }
                    )
                }
            )
            
            FilledIconButton(
                onClick = onSendClick,
                enabled = enabled && !isSending,
                modifier = Modifier.size(56.dp)
            ) {
                if (isSending) {
                    CircularProgressIndicator(
                        modifier = Modifier.size(24.dp),
                        color = MaterialTheme.colorScheme.onPrimary
                    )
                } else {
                    Icon(
                        imageVector = Icons.AutoMirrored.Filled.Send,
                        contentDescription = "Send message"
                    )
                }
            }
        }
    }
}

/**
 * Individual chat message item.
 * Requirements: 10.4, 10.7
 */
@Composable
fun ChatMessageItem(
    message: ChatMessage,
    isOwnMessage: Boolean
) {
    val alignment = if (isOwnMessage) Alignment.End else Alignment.Start
    val backgroundColor = if (isOwnMessage) {
        MaterialTheme.colorScheme.primaryContainer
    } else {
        MaterialTheme.colorScheme.surfaceVariant
    }
    val textColor = if (isOwnMessage) {
        MaterialTheme.colorScheme.onPrimaryContainer
    } else {
        MaterialTheme.colorScheme.onSurfaceVariant
    }
    
    Column(
        modifier = Modifier.fillMaxWidth(),
        horizontalAlignment = alignment
    ) {
        Surface(
            shape = RoundedCornerShape(
                topStart = 16.dp,
                topEnd = 16.dp,
                bottomStart = if (isOwnMessage) 16.dp else 4.dp,
                bottomEnd = if (isOwnMessage) 4.dp else 16.dp
            ),
            color = backgroundColor,
            modifier = Modifier.widthIn(max = 280.dp)
        ) {
            Column(
                modifier = Modifier.padding(12.dp)
            ) {
                Text(
                    text = message.message,
                    style = MaterialTheme.typography.bodyMedium,
                    color = textColor
                )
                
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(top = 4.dp),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(
                        text = formatTimestamp(message.timestamp),
                        style = MaterialTheme.typography.bodySmall,
                        color = textColor.copy(alpha = 0.7f)
                    )
                    
                    if (isOwnMessage) {
                        MessageStatusIcon(status = message.status)
                    }
                }
            }
        }
    }
}

/**
 * Message status icon (sent, delivered, read).
 * Requirements: 10.7
 */
@Composable
fun MessageStatusIcon(status: MessageStatus) {
    val statusText = when (status) {
        MessageStatus.SENT -> "✓"
        MessageStatus.DELIVERED -> "✓✓"
        MessageStatus.READ -> "✓✓"
    }
    
    val statusColor = when (status) {
        MessageStatus.SENT -> MaterialTheme.colorScheme.onPrimaryContainer.copy(alpha = 0.5f)
        MessageStatus.DELIVERED -> MaterialTheme.colorScheme.onPrimaryContainer.copy(alpha = 0.7f)
        MessageStatus.READ -> MaterialTheme.colorScheme.primary
    }
    
    Text(
        text = statusText,
        style = MaterialTheme.typography.bodySmall,
        color = statusColor,
        modifier = Modifier.padding(start = 4.dp)
    )
}

/**
 * Format timestamp to readable time string.
 */
private fun formatTimestamp(timestamp: Long): String {
    val date = Date(timestamp)
    val now = Date()
    val calendar = Calendar.getInstance()
    
    calendar.time = date
    val messageDay = calendar.get(Calendar.DAY_OF_YEAR)
    val messageYear = calendar.get(Calendar.YEAR)
    
    calendar.time = now
    val currentDay = calendar.get(Calendar.DAY_OF_YEAR)
    val currentYear = calendar.get(Calendar.YEAR)
    
    return when {
        messageDay == currentDay && messageYear == currentYear -> {
            // Today - show time only
            SimpleDateFormat("HH:mm", Locale.getDefault()).format(date)
        }
        messageDay == currentDay - 1 && messageYear == currentYear -> {
            // Yesterday
            "Yesterday ${SimpleDateFormat("HH:mm", Locale.getDefault()).format(date)}"
        }
        else -> {
            // Older - show date and time
            SimpleDateFormat("MMM dd, HH:mm", Locale.getDefault()).format(date)
        }
    }
}
