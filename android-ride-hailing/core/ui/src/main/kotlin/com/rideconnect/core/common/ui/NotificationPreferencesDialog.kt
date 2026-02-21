package com.rideconnect.core.common.ui

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.rideconnect.core.domain.model.NotificationPreferences

@Composable
fun NotificationPreferencesDialog(
    preferences: NotificationPreferences,
    onSave: (NotificationPreferences) -> Unit,
    onDismiss: () -> Unit,
    isDriverApp: Boolean = false
) {
    var currentPreferences by remember { mutableStateOf(preferences) }
    
    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text("Notification Preferences") },
        text = {
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .verticalScroll(rememberScrollState())
            ) {
                Text(
                    text = "Choose which notifications you want to receive",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                    modifier = Modifier.padding(bottom = 16.dp)
                )
                
                // Ride notifications
                if (!isDriverApp) {
                    NotificationToggle(
                        title = "Ride Accepted",
                        description = "When a driver accepts your ride",
                        checked = currentPreferences.rideAccepted,
                        onCheckedChange = { 
                            currentPreferences = currentPreferences.copy(rideAccepted = it)
                        }
                    )
                    
                    NotificationToggle(
                        title = "Driver Arriving",
                        description = "When driver is on the way",
                        checked = currentPreferences.driverArriving,
                        onCheckedChange = { 
                            currentPreferences = currentPreferences.copy(driverArriving = it)
                        }
                    )
                    
                    NotificationToggle(
                        title = "Driver Arrived",
                        description = "When driver reaches pickup location",
                        checked = currentPreferences.driverArrived,
                        onCheckedChange = { 
                            currentPreferences = currentPreferences.copy(driverArrived = it)
                        }
                    )
                }
                
                if (isDriverApp) {
                    NotificationToggle(
                        title = "New Ride Requests",
                        description = "When a new ride request is available",
                        checked = currentPreferences.newRideRequest,
                        onCheckedChange = { 
                            currentPreferences = currentPreferences.copy(newRideRequest = it)
                        }
                    )
                }
                
                NotificationToggle(
                    title = "Ride Started",
                    description = "When the ride begins",
                    checked = currentPreferences.rideStarted,
                    onCheckedChange = { 
                        currentPreferences = currentPreferences.copy(rideStarted = it)
                    }
                )
                
                NotificationToggle(
                    title = "Ride Completed",
                    description = "When the ride is finished",
                    checked = currentPreferences.rideCompleted,
                    onCheckedChange = { 
                        currentPreferences = currentPreferences.copy(rideCompleted = it)
                    }
                )
                
                NotificationToggle(
                    title = "Ride Cancelled",
                    description = "When a ride is cancelled",
                    checked = currentPreferences.rideCancelled,
                    onCheckedChange = { 
                        currentPreferences = currentPreferences.copy(rideCancelled = it)
                    }
                )
                
                NotificationToggle(
                    title = "Chat Messages",
                    description = "When you receive a new message",
                    checked = currentPreferences.chatMessage,
                    onCheckedChange = { 
                        currentPreferences = currentPreferences.copy(chatMessage = it)
                    }
                )
                
                NotificationToggle(
                    title = "Payment Success",
                    description = "When payment is successful",
                    checked = currentPreferences.paymentSuccess,
                    onCheckedChange = { 
                        currentPreferences = currentPreferences.copy(paymentSuccess = it)
                    }
                )
                
                NotificationToggle(
                    title = "Payment Failed",
                    description = "When payment fails",
                    checked = currentPreferences.paymentFailed,
                    onCheckedChange = { 
                        currentPreferences = currentPreferences.copy(paymentFailed = it)
                    }
                )
                
                NotificationToggle(
                    title = "Scheduled Ride Reminders",
                    description = "Reminders for scheduled rides",
                    checked = currentPreferences.scheduledRideReminder,
                    onCheckedChange = { 
                        currentPreferences = currentPreferences.copy(scheduledRideReminder = it)
                    }
                )
            }
        },
        confirmButton = {
            TextButton(onClick = { onSave(currentPreferences) }) {
                Text("Save")
            }
        },
        dismissButton = {
            TextButton(onClick = onDismiss) {
                Text("Cancel")
            }
        }
    )
}

@Composable
private fun NotificationToggle(
    title: String,
    description: String,
    checked: Boolean,
    onCheckedChange: (Boolean) -> Unit
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 8.dp),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically
    ) {
        Column(modifier = Modifier.weight(1f)) {
            Text(
                text = title,
                style = MaterialTheme.typography.bodyMedium
            )
            Text(
                text = description,
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }
        
        Switch(
            checked = checked,
            onCheckedChange = onCheckedChange
        )
    }
}
