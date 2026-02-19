package com.rideconnect.core.common.ui

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import com.rideconnect.core.domain.model.Location
import com.rideconnect.core.domain.model.ScheduledRide
import com.rideconnect.core.domain.model.ScheduledRideStatus
import com.rideconnect.core.domain.viewmodel.ScheduledRideViewModel
import java.text.SimpleDateFormat
import java.util.*

/**
 * Screen for viewing and managing scheduled rides.
 * 
 * Requirements: 4.1, 4.2, 4.3, 4.6, 4.7
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ScheduledRidesScreen(
    viewModel: ScheduledRideViewModel = hiltViewModel(),
    onScheduleNewRide: () -> Unit = {},
    onRideClick: (ScheduledRide) -> Unit = {}
) {
    val scheduledRides by viewModel.scheduledRides.collectAsState()
    val isLoading by viewModel.isLoading.collectAsState()
    val error by viewModel.error.collectAsState()

    var showCancelDialog by remember { mutableStateOf<ScheduledRide?>(null) }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Scheduled Rides") },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = MaterialTheme.colorScheme.primaryContainer,
                    titleContentColor = MaterialTheme.colorScheme.onPrimaryContainer
                )
            )
        },
        floatingActionButton = {
            FloatingActionButton(
                onClick = onScheduleNewRide,
                containerColor = MaterialTheme.colorScheme.primary
            ) {
                Icon(Icons.Default.Add, contentDescription = "Schedule New Ride")
            }
        }
    ) { paddingValues ->
        Box(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
        ) {
            when {
                isLoading && scheduledRides.isEmpty() -> {
                    CircularProgressIndicator(
                        modifier = Modifier.align(Alignment.Center)
                    )
                }
                scheduledRides.isEmpty() -> {
                    EmptyScheduledRidesView(
                        onScheduleRide = onScheduleNewRide,
                        modifier = Modifier.align(Alignment.Center)
                    )
                }
                else -> {
                    LazyColumn(
                        modifier = Modifier.fillMaxSize(),
                        contentPadding = PaddingValues(16.dp),
                        verticalArrangement = Arrangement.spacedBy(12.dp)
                    ) {
                        items(scheduledRides, key = { it.id }) { ride ->
                            ScheduledRideCard(
                                ride = ride,
                                onClick = { onRideClick(ride) },
                                onCancel = { showCancelDialog = ride }
                            )
                        }
                    }
                }
            }

            // Error snackbar
            AnimatedVisibility(
                visible = error != null,
                enter = fadeIn(),
                exit = fadeOut(),
                modifier = Modifier.align(Alignment.BottomCenter)
            ) {
                Snackbar(
                    modifier = Modifier.padding(16.dp),
                    action = {
                        TextButton(onClick = { viewModel.clearError() }) {
                            Text("Dismiss")
                        }
                    }
                ) {
                    Text(error ?: "")
                }
            }
        }
    }

    // Cancel confirmation dialog
    showCancelDialog?.let { ride ->
        CancelScheduledRideDialog(
            ride = ride,
            onConfirm = { reason ->
                viewModel.cancelScheduledRide(ride.id, reason)
                showCancelDialog = null
            },
            onDismiss = { showCancelDialog = null }
        )
    }
}

@Composable
private fun ScheduledRideCard(
    ride: ScheduledRide,
    onClick: () -> Unit,
    onCancel: () -> Unit
) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .clickable(onClick = onClick),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surface
        )
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp)
        ) {
            // Status badge
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                StatusBadge(status = ride.status)
                
                if (ride.status == ScheduledRideStatus.SCHEDULED) {
                    IconButton(onClick = onCancel) {
                        Icon(
                            Icons.Default.Close,
                            contentDescription = "Cancel Ride",
                            tint = MaterialTheme.colorScheme.error
                        )
                    }
                }
            }

            Spacer(modifier = Modifier.height(12.dp))

            // Scheduled time
            Row(
                verticalAlignment = Alignment.CenterVertically
            ) {
                Icon(
                    Icons.Default.Schedule,
                    contentDescription = null,
                    tint = MaterialTheme.colorScheme.primary,
                    modifier = Modifier.size(20.dp)
                )
                Spacer(modifier = Modifier.width(8.dp))
                Text(
                    text = formatScheduledTime(ride.scheduledTime),
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold
                )
            }

            Spacer(modifier = Modifier.height(12.dp))

            // Pickup location
            LocationRow(
                icon = Icons.Default.LocationOn,
                label = "Pickup",
                address = ride.pickupLocation.address ?: "Unknown location",
                iconTint = MaterialTheme.colorScheme.primary
            )

            Spacer(modifier = Modifier.height(8.dp))

            // Dropoff location
            LocationRow(
                icon = Icons.Default.Place,
                label = "Dropoff",
                address = ride.dropoffLocation.address ?: "Unknown location",
                iconTint = MaterialTheme.colorScheme.secondary
            )

            // Fare and distance
            ride.fare?.let { fare ->
                Spacer(modifier = Modifier.height(12.dp))
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {
                    Text(
                        text = "Estimated Fare: ₹${String.format("%.2f", fare)}",
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                    ride.distance?.let { distance ->
                        Text(
                            text = "${String.format("%.1f", distance)} km",
                            style = MaterialTheme.typography.bodyMedium,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }
                }
            }
        }
    }
}

@Composable
private fun StatusBadge(status: ScheduledRideStatus) {
    val (text, color) = when (status) {
        ScheduledRideStatus.SCHEDULED -> "Scheduled" to MaterialTheme.colorScheme.primary
        ScheduledRideStatus.CONFIRMED -> "Confirmed" to MaterialTheme.colorScheme.tertiary
        ScheduledRideStatus.IN_PROGRESS -> "In Progress" to MaterialTheme.colorScheme.secondary
        ScheduledRideStatus.COMPLETED -> "Completed" to MaterialTheme.colorScheme.outline
        ScheduledRideStatus.CANCELLED -> "Cancelled" to MaterialTheme.colorScheme.error
    }

    Box(
        modifier = Modifier
            .clip(RoundedCornerShape(12.dp))
            .background(color.copy(alpha = 0.1f))
            .padding(horizontal = 12.dp, vertical = 6.dp)
    ) {
        Text(
            text = text,
            style = MaterialTheme.typography.labelMedium,
            color = color,
            fontWeight = FontWeight.Medium
        )
    }
}

@Composable
private fun LocationRow(
    icon: androidx.compose.ui.graphics.vector.ImageVector,
    label: String,
    address: String,
    iconTint: androidx.compose.ui.graphics.Color
) {
    Row(
        verticalAlignment = Alignment.Top
    ) {
        Icon(
            icon,
            contentDescription = label,
            tint = iconTint,
            modifier = Modifier.size(20.dp)
        )
        Spacer(modifier = Modifier.width(8.dp))
        Column {
            Text(
                text = label,
                style = MaterialTheme.typography.labelSmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
            Text(
                text = address,
                style = MaterialTheme.typography.bodyMedium
            )
        }
    }
}

@Composable
private fun EmptyScheduledRidesView(
    onScheduleRide: () -> Unit,
    modifier: Modifier = Modifier
) {
    Column(
        modifier = modifier.padding(32.dp),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Icon(
            Icons.Default.Schedule,
            contentDescription = null,
            modifier = Modifier.size(80.dp),
            tint = MaterialTheme.colorScheme.outline
        )
        Spacer(modifier = Modifier.height(16.dp))
        Text(
            text = "No Scheduled Rides",
            style = MaterialTheme.typography.titleLarge,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
        Spacer(modifier = Modifier.height(8.dp))
        Text(
            text = "Schedule rides up to 7 days in advance",
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
        Spacer(modifier = Modifier.height(24.dp))
        Button(onClick = onScheduleRide) {
            Icon(Icons.Default.Add, contentDescription = null)
            Spacer(modifier = Modifier.width(8.dp))
            Text("Schedule a Ride")
        }
    }
}

@Composable
private fun CancelScheduledRideDialog(
    ride: ScheduledRide,
    onConfirm: (String) -> Unit,
    onDismiss: () -> Unit
) {
    var selectedReason by remember { mutableStateOf("") }
    val cancellationReasons = listOf(
        "Change of plans",
        "Found alternative transport",
        "Wrong time selected",
        "Wrong location selected",
        "Other"
    )

    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text("Cancel Scheduled Ride") },
        text = {
            Column {
                Text(
                    text = "Are you sure you want to cancel this scheduled ride?",
                    style = MaterialTheme.typography.bodyMedium
                )
                Spacer(modifier = Modifier.height(16.dp))
                Text(
                    text = "Reason for cancellation:",
                    style = MaterialTheme.typography.labelMedium
                )
                Spacer(modifier = Modifier.height(8.dp))
                cancellationReasons.forEach { reason ->
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .clickable { selectedReason = reason }
                            .padding(vertical = 8.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        RadioButton(
                            selected = selectedReason == reason,
                            onClick = { selectedReason = reason }
                        )
                        Spacer(modifier = Modifier.width(8.dp))
                        Text(text = reason)
                    }
                }
            }
        },
        confirmButton = {
            TextButton(
                onClick = { onConfirm(selectedReason.ifEmpty { "No reason provided" }) },
                enabled = selectedReason.isNotEmpty()
            ) {
                Text("Cancel Ride")
            }
        },
        dismissButton = {
            TextButton(onClick = onDismiss) {
                Text("Keep Ride")
            }
        }
    )
}

private fun formatScheduledTime(timestamp: Long): String {
    val dateFormat = SimpleDateFormat("EEE, MMM dd, yyyy 'at' hh:mm a", Locale.getDefault())
    return dateFormat.format(Date(timestamp))
}
