package com.rideconnect.core.common.ui

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp

/**
 * Notification type enum for UI
 */
enum class NotificationType {
    RIDE_REQUEST,
    RIDE_ACCEPTED,
    RIDE_STARTED,
    RIDE_COMPLETED,
    RIDE_CANCELLED,
    NEW_MESSAGE,
    SCHEDULED_RIDE_REMINDER,
    PROMOTION,
    GENERAL
}

/**
 * Screen for managing notification preferences.
 * Requirements: 19.7, 27.2
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun NotificationPreferencesScreen(
    preferences: Map<NotificationType, Boolean>,
    onPreferenceChanged: (NotificationType, Boolean) -> Unit,
    onResetToDefaults: () -> Unit,
    onNavigateBack: () -> Unit
) {
    var currentPreferences by remember {
        mutableStateOf(preferences)
    }
    
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Notification Preferences") },
                navigationIcon = {
                    IconButton(onClick = onNavigateBack) {
                        Icon(Icons.Default.ArrowBack, "Back")
                    }
                }
            )
        }
    ) { padding ->
        LazyColumn(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding),
            contentPadding = PaddingValues(16.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            item {
                Text(
                    text = "Choose which notifications you want to receive",
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                    modifier = Modifier.padding(bottom = 8.dp)
                )
            }
            
            items(NotificationType.values().toList()) { type ->
                NotificationPreferenceItem(
                    type = type,
                    enabled = currentPreferences[type] ?: true,
                    onToggle = { enabled ->
                        onPreferenceChanged(type, enabled)
                        currentPreferences = currentPreferences.toMutableMap().apply {
                            put(type, enabled)
                        }
                    }
                )
            }
            
            item {
                Spacer(modifier = Modifier.height(16.dp))
                
                OutlinedButton(
                    onClick = {
                        onResetToDefaults()
                        currentPreferences = NotificationType.values().associateWith { true }
                    },
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Text("Reset to Defaults")
                }
            }
        }
    }
}

@Composable
private fun NotificationPreferenceItem(
    type: NotificationType,
    enabled: Boolean,
    onToggle: (Boolean) -> Unit
) {
    Card(
        modifier = Modifier.fillMaxWidth()
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = getNotificationTypeTitle(type),
                    style = MaterialTheme.typography.titleMedium
                )
                Text(
                    text = getNotificationTypeDescription(type),
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
            
            Switch(
                checked = enabled,
                onCheckedChange = onToggle
            )
        }
    }
}

private fun getNotificationTypeTitle(type: NotificationType): String {
    return when (type) {
        NotificationType.RIDE_REQUEST -> "Ride Requests"
        NotificationType.RIDE_ACCEPTED -> "Ride Accepted"
        NotificationType.RIDE_STARTED -> "Ride Started"
        NotificationType.RIDE_COMPLETED -> "Ride Completed"
        NotificationType.RIDE_CANCELLED -> "Ride Cancelled"
        NotificationType.NEW_MESSAGE -> "New Messages"
        NotificationType.SCHEDULED_RIDE_REMINDER -> "Ride Reminders"
        NotificationType.PROMOTION -> "Promotions"
        NotificationType.GENERAL -> "General Notifications"
    }
}

private fun getNotificationTypeDescription(type: NotificationType): String {
    return when (type) {
        NotificationType.RIDE_REQUEST -> "Get notified when a new ride request is available"
        NotificationType.RIDE_ACCEPTED -> "Get notified when your ride is accepted"
        NotificationType.RIDE_STARTED -> "Get notified when your ride has started"
        NotificationType.RIDE_COMPLETED -> "Get notified when your ride is completed"
        NotificationType.RIDE_CANCELLED -> "Get notified if your ride is cancelled"
        NotificationType.NEW_MESSAGE -> "Get notified when you receive a new message"
        NotificationType.SCHEDULED_RIDE_REMINDER -> "Get reminders for your scheduled rides"
        NotificationType.PROMOTION -> "Receive promotional offers and updates"
        NotificationType.GENERAL -> "Receive general app notifications"
    }
}
