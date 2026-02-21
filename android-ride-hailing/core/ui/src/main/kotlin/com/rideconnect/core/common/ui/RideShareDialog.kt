package com.rideconnect.core.common.ui

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.selection.toggleable
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Close
import androidx.compose.material.icons.filled.Share
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.semantics.Role
import androidx.compose.ui.unit.dp
import com.rideconnect.core.domain.model.EmergencyContact
import com.rideconnect.core.domain.viewmodel.ShareRideState

/**
 * Dialog for sharing ride tracking link with emergency contacts.
 * Requirements: 9.4
 */
@Composable
fun RideShareDialog(
    emergencyContacts: List<EmergencyContact>,
    shareRideState: ShareRideState,
    onShareRide: (List<String>) -> Unit,
    onDismiss: () -> Unit,
    modifier: Modifier = Modifier
) {
    var selectedContactIds by remember { mutableStateOf(setOf<String>()) }
    
    AlertDialog(
        onDismissRequest = onDismiss,
        title = {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text("Share Ride Tracking")
                IconButton(onClick = onDismiss) {
                    Icon(Icons.Default.Close, contentDescription = "Close")
                }
            }
        },
        text = {
            Column(
                modifier = Modifier.fillMaxWidth()
            ) {
                when (shareRideState) {
                    is ShareRideState.Idle -> {
                        if (emergencyContacts.isEmpty()) {
                            Text(
                                text = "No emergency contacts available. Please add contacts first.",
                                style = MaterialTheme.typography.bodyMedium,
                                color = MaterialTheme.colorScheme.onSurfaceVariant
                            )
                        } else {
                            Text(
                                text = "Select contacts to share your live ride tracking link:",
                                style = MaterialTheme.typography.bodyMedium,
                                modifier = Modifier.padding(bottom = 16.dp)
                            )
                            
                            LazyColumn(
                                modifier = Modifier.fillMaxWidth(),
                                verticalArrangement = Arrangement.spacedBy(8.dp)
                            ) {
                                items(emergencyContacts) { contact ->
                                    ContactCheckboxItem(
                                        contact = contact,
                                        isSelected = selectedContactIds.contains(contact.id),
                                        onToggle = { isSelected ->
                                            selectedContactIds = if (isSelected) {
                                                selectedContactIds + contact.id
                                            } else {
                                                selectedContactIds - contact.id
                                            }
                                        }
                                    )
                                }
                            }
                        }
                    }
                    
                    is ShareRideState.Sharing -> {
                        Box(
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(32.dp),
                            contentAlignment = Alignment.Center
                        ) {
                            Column(
                                horizontalAlignment = Alignment.CenterHorizontally,
                                verticalArrangement = Arrangement.spacedBy(16.dp)
                            ) {
                                CircularProgressIndicator()
                                Text("Sharing ride...")
                            }
                        }
                    }
                    
                    is ShareRideState.Success -> {
                        Column(
                            modifier = Modifier.fillMaxWidth(),
                            verticalArrangement = Arrangement.spacedBy(16.dp)
                        ) {
                            Icon(
                                imageVector = Icons.Default.Share,
                                contentDescription = null,
                                tint = MaterialTheme.colorScheme.primary,
                                modifier = Modifier
                                    .size(48.dp)
                                    .align(Alignment.CenterHorizontally)
                            )
                            
                            Text(
                                text = "Ride tracking link shared successfully!",
                                style = MaterialTheme.typography.titleMedium,
                                color = MaterialTheme.colorScheme.primary
                            )
                            
                            Text(
                                text = "Your selected contacts will receive a link to track your ride in real-time.",
                                style = MaterialTheme.typography.bodyMedium,
                                color = MaterialTheme.colorScheme.onSurfaceVariant
                            )
                            
                            OutlinedCard(
                                modifier = Modifier.fillMaxWidth()
                            ) {
                                Text(
                                    text = shareRideState.shareUrl,
                                    style = MaterialTheme.typography.bodySmall,
                                    modifier = Modifier.padding(12.dp)
                                )
                            }
                        }
                    }
                    
                    is ShareRideState.Error -> {
                        Column(
                            modifier = Modifier.fillMaxWidth(),
                            verticalArrangement = Arrangement.spacedBy(8.dp)
                        ) {
                            Text(
                                text = "Failed to share ride",
                                style = MaterialTheme.typography.titleMedium,
                                color = MaterialTheme.colorScheme.error
                            )
                            Text(
                                text = shareRideState.message,
                                style = MaterialTheme.typography.bodyMedium,
                                color = MaterialTheme.colorScheme.onSurfaceVariant
                            )
                        }
                    }
                }
            }
        },
        confirmButton = {
            when (shareRideState) {
                is ShareRideState.Idle -> {
                    if (emergencyContacts.isNotEmpty()) {
                        Button(
                            onClick = {
                                if (selectedContactIds.isNotEmpty()) {
                                    onShareRide(selectedContactIds.toList())
                                }
                            },
                            enabled = selectedContactIds.isNotEmpty()
                        ) {
                            Icon(
                                imageVector = Icons.Default.Share,
                                contentDescription = null,
                                modifier = Modifier.size(18.dp)
                            )
                            Spacer(modifier = Modifier.width(8.dp))
                            Text("Share")
                        }
                    }
                }
                
                is ShareRideState.Success -> {
                    Button(onClick = onDismiss) {
                        Text("Done")
                    }
                }
                
                is ShareRideState.Error -> {
                    Button(
                        onClick = {
                            if (selectedContactIds.isNotEmpty()) {
                                onShareRide(selectedContactIds.toList())
                            }
                        },
                        enabled = selectedContactIds.isNotEmpty()
                    ) {
                        Text("Retry")
                    }
                }
                
                else -> {}
            }
        },
        dismissButton = {
            if (shareRideState !is ShareRideState.Sharing) {
                TextButton(onClick = onDismiss) {
                    Text("Cancel")
                }
            }
        },
        modifier = modifier
    )
}

/**
 * Checkbox item for selecting an emergency contact.
 */
@Composable
private fun ContactCheckboxItem(
    contact: EmergencyContact,
    isSelected: Boolean,
    onToggle: (Boolean) -> Unit,
    modifier: Modifier = Modifier
) {
    Surface(
        modifier = modifier
            .fillMaxWidth()
            .toggleable(
                value = isSelected,
                role = Role.Checkbox,
                onValueChange = onToggle
            ),
        shape = MaterialTheme.shapes.small,
        tonalElevation = if (isSelected) 4.dp else 0.dp
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(12.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Checkbox(
                checked = isSelected,
                onCheckedChange = null // handled by toggleable
            )
            
            Spacer(modifier = Modifier.width(12.dp))
            
            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = contact.name,
                    style = MaterialTheme.typography.bodyLarge
                )
                Text(
                    text = contact.phoneNumber,
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
                contact.relationship?.let { relationship ->
                    Text(
                        text = relationship,
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
            }
        }
    }
}
