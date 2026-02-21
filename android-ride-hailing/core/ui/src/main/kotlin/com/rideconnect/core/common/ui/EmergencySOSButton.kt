package com.rideconnect.core.common.ui

import androidx.compose.foundation.layout.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Warning
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.window.Dialog
import androidx.hilt.navigation.compose.hiltViewModel
import com.rideconnect.core.common.accessibility.AccessibilityUtils
import com.rideconnect.core.common.accessibility.accessibleTouchTarget
import com.rideconnect.core.domain.viewmodel.EmergencyViewModel
import com.rideconnect.core.domain.viewmodel.SOSState

/**
 * Prominent SOS button for emergency situations.
 * Requirements: 9.1, 9.3, 9.5
 */
@Composable
fun EmergencySOSButton(
    rideId: String,
    modifier: Modifier = Modifier,
    viewModel: EmergencyViewModel = hiltViewModel()
) {
    val context = LocalContext.current
    val sosState by viewModel.sosState.collectAsState()
    val sosActive by viewModel.sosActive.collectAsState()
    var showConfirmDialog by remember { mutableStateOf(false) }
    
    // SOS Button with accessibility support
    Button(
        onClick = {
            // Provide strong haptic feedback for critical action
            AccessibilityUtils.provideStrongHapticFeedback(context)
            showConfirmDialog = true
        },
        modifier = modifier
            .fillMaxWidth()
            .height(56.dp)
            .accessibleTouchTarget()
            .semantics {
                contentDescription = if (sosActive) {
                    "Emergency SOS is active. Tap to view details"
                } else {
                    "Emergency SOS button. Tap to send alert to emergency contacts and authorities"
                }
            },
        colors = ButtonDefaults.buttonColors(
            containerColor = if (sosActive) Color(0xFFFF6B6B) else Color(0xFFFF3B30),
            contentColor = Color.White
        ),
        enabled = sosState !is SOSState.Triggering
    ) {
        if (sosState is SOSState.Triggering) {
            CircularProgressIndicator(
                modifier = Modifier
                    .size(24.dp)
                    .semantics { contentDescription = "Activating emergency SOS" },
                color = Color.White
            )
            Spacer(modifier = Modifier.width(8.dp))
        } else {
            Icon(
                imageVector = Icons.Default.Warning,
                contentDescription = null, // Handled by button's content description
                modifier = Modifier.size(24.dp)
            )
            Spacer(modifier = Modifier.width(8.dp))
        }
        Text(
            text = if (sosActive) "SOS ACTIVE" else "EMERGENCY SOS",
            style = MaterialTheme.typography.titleMedium,
            fontWeight = FontWeight.Bold
        )
    }
    
    // Confirmation Dialog
    if (showConfirmDialog) {
        SOSConfirmationDialog(
            onConfirm = {
                showConfirmDialog = false
                viewModel.triggerSOS(rideId)
            },
            onDismiss = { showConfirmDialog = false }
        )
    }
    
    // Error Snackbar
    val error by viewModel.error.collectAsState()
    error?.let { errorMessage ->
        LaunchedEffect(errorMessage) {
            // Show error in parent composable's snackbar
        }
    }
}

/**
 * Confirmation dialog for SOS activation.
 * Requirements: 9.3
 */
@Composable
fun SOSConfirmationDialog(
    onConfirm: () -> Unit,
    onDismiss: () -> Unit
) {
    val context = LocalContext.current
    
    AlertDialog(
        onDismissRequest = onDismiss,
        icon = {
            Icon(
                imageVector = Icons.Default.Warning,
                contentDescription = "Emergency warning icon",
                tint = Color(0xFFFF3B30),
                modifier = Modifier.size(48.dp)
            )
        },
        title = {
            Text(
                text = "Activate Emergency SOS?",
                style = MaterialTheme.typography.headlineSmall,
                fontWeight = FontWeight.Bold,
                textAlign = TextAlign.Center
            )
        },
        text = {
            Column(
                modifier = Modifier.semantics {
                    contentDescription = "Emergency SOS will alert emergency services, " +
                            "notify your emergency contacts, share your live location, " +
                            "and record incident details. Only use in genuine emergencies."
                }
            ) {
                Text(
                    text = "This will:",
                    style = MaterialTheme.typography.bodyLarge,
                    fontWeight = FontWeight.SemiBold
                )
                Spacer(modifier = Modifier.height(8.dp))
                Text("• Alert emergency services")
                Text("• Notify your emergency contacts")
                Text("• Share your live location")
                Text("• Record incident details")
                Spacer(modifier = Modifier.height(8.dp))
                Text(
                    text = "Only use in genuine emergencies.",
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.error
                )
            }
        },
        confirmButton = {
            Button(
                onClick = {
                    AccessibilityUtils.provideHapticFeedback(context)
                    onConfirm()
                },
                modifier = Modifier
                    .accessibleTouchTarget()
                    .semantics {
                        contentDescription = "Activate emergency SOS now"
                    },
                colors = ButtonDefaults.buttonColors(
                    containerColor = Color(0xFFFF3B30)
                )
            ) {
                Text("ACTIVATE SOS")
            }
        },
        dismissButton = {
            TextButton(
                onClick = onDismiss,
                modifier = Modifier
                    .accessibleTouchTarget()
                    .semantics {
                        contentDescription = "Cancel emergency SOS activation"
                    }
            ) {
                Text("Cancel")
            }
        }
    )
}

/**
 * Emergency contacts list with call buttons.
 * Requirements: 9.5
 */
@Composable
fun EmergencyContactsList(
    modifier: Modifier = Modifier,
    viewModel: EmergencyViewModel = hiltViewModel(),
    onCallContact: (String) -> Unit
) {
    val contacts by viewModel.emergencyContacts.collectAsState()
    
    Column(modifier = modifier) {
        Text(
            text = "Emergency Contacts",
            style = MaterialTheme.typography.titleMedium,
            fontWeight = FontWeight.Bold,
            modifier = Modifier.padding(bottom = 8.dp)
        )
        
        if (contacts.isEmpty()) {
            Card(
                modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(
                    containerColor = MaterialTheme.colorScheme.surfaceVariant
                )
            ) {
                Text(
                    text = "No emergency contacts added",
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                    modifier = Modifier.padding(16.dp)
                )
            }
        } else {
            contacts.forEach { contact ->
                EmergencyContactItem(
                    contact = contact,
                    onCallClick = { onCallContact(contact.phoneNumber) }
                )
                Spacer(modifier = Modifier.height(8.dp))
            }
        }
    }
}

/**
 * Individual emergency contact item with call button.
 */
@Composable
fun EmergencyContactItem(
    contact: com.rideconnect.core.domain.model.EmergencyContact,
    onCallClick: () -> Unit
) {
    val context = LocalContext.current
    
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .semantics {
                contentDescription = "Emergency contact: ${contact.name}, " +
                        "phone number ${contact.phoneNumber}" +
                        (contact.relationship?.let { ", relationship: $it" } ?: "")
            },
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surface
        ),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
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
                    text = contact.name,
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.SemiBold
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
            
            Button(
                onClick = {
                    AccessibilityUtils.provideHapticFeedback(context)
                    onCallClick()
                },
                modifier = Modifier
                    .accessibleTouchTarget()
                    .semantics {
                        contentDescription = "Call ${contact.name} at ${contact.phoneNumber}"
                    },
                colors = ButtonDefaults.buttonColors(
                    containerColor = Color(0xFF34C759)
                )
            ) {
                Text("Call")
            }
        }
    }
}
