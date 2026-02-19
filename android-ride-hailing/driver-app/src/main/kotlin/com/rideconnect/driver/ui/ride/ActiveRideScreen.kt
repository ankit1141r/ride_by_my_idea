package com.rideconnect.driver.ui.ride

import android.content.Context
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.rideconnect.core.common.navigation.NavigationHelper
import com.rideconnect.core.domain.model.Ride
import com.rideconnect.core.domain.model.RideStatus
import com.rideconnect.core.domain.viewmodel.DriverViewModel

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ActiveRideScreen(
    viewModel: DriverViewModel,
    onNavigateBack: () -> Unit,
    modifier: Modifier = Modifier
) {
    val uiState by viewModel.uiState.collectAsState()
    val context = LocalContext.current
    val ride = uiState.activeRide
    
    var showCancelDialog by remember { mutableStateOf(false) }
    
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Active Ride") },
                navigationIcon = {
                    IconButton(onClick = onNavigateBack) {
                        Icon(Icons.Default.ArrowBack, contentDescription = "Back")
                    }
                }
            )
        }
    ) { paddingValues ->
        if (ride != null) {
            Column(
                modifier = modifier
                    .fillMaxSize()
                    .padding(paddingValues)
                    .padding(16.dp),
                verticalArrangement = Arrangement.spacedBy(16.dp)
            ) {
                // Ride Status Card
                RideStatusCard(ride = ride)
                
                // Navigation Card
                NavigationCard(
                    ride = ride,
                    context = context
                )
                
                // Rider Contact Card
                RiderContactCard(ride = ride)
                
                Spacer(modifier = Modifier.weight(1f))
                
                // Action Buttons
                RideActionButtons(
                    ride = ride,
                    onStartRide = { viewModel.startRide() },
                    onCompleteRide = { viewModel.completeRide() },
                    onCancelRide = { showCancelDialog = true },
                    isLoading = uiState.isLoading
                )
                
                // Error Message
                if (uiState.error != null) {
                    Card(
                        colors = CardDefaults.cardColors(
                            containerColor = MaterialTheme.colorScheme.errorContainer
                        ),
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Row(
                            modifier = Modifier.padding(12.dp),
                            horizontalArrangement = Arrangement.spacedBy(8.dp),
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Icon(
                                Icons.Default.Warning,
                                contentDescription = null,
                                tint = MaterialTheme.colorScheme.error
                            )
                            Text(
                                text = uiState.error ?: "",
                                color = MaterialTheme.colorScheme.onErrorContainer,
                                style = MaterialTheme.typography.bodyMedium
                            )
                        }
                    }
                }
            }
            
            // Cancel Dialog
            if (showCancelDialog) {
                CancelRideDialog(
                    onDismiss = { showCancelDialog = false },
                    onConfirm = { reason ->
                        viewModel.cancelRide(reason)
                        showCancelDialog = false
                    }
                )
            }
        } else {
            // No active ride
            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(paddingValues),
                contentAlignment = Alignment.Center
            ) {
                Column(
                    horizontalAlignment = Alignment.CenterHorizontally,
                    verticalArrangement = Arrangement.spacedBy(16.dp)
                ) {
                    Icon(
                        imageVector = Icons.Default.DirectionsCar,
                        contentDescription = null,
                        modifier = Modifier.size(64.dp),
                        tint = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                    Text(
                        text = "No Active Ride",
                        style = MaterialTheme.typography.titleLarge,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                    Button(onClick = onNavigateBack) {
                        Text("Go Back")
                    }
                }
            }
        }
    }
}

@Composable
private fun RideStatusCard(
    ride: Ride,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = when (ride.status) {
                RideStatus.ACCEPTED, RideStatus.DRIVER_ARRIVING -> MaterialTheme.colorScheme.primaryContainer
                RideStatus.ARRIVED -> MaterialTheme.colorScheme.secondaryContainer
                RideStatus.IN_PROGRESS -> MaterialTheme.colorScheme.tertiaryContainer
                else -> MaterialTheme.colorScheme.surfaceVariant
            }
        )
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            horizontalArrangement = Arrangement.spacedBy(12.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Box(
                modifier = Modifier
                    .size(48.dp)
                    .clip(CircleShape)
                    .background(MaterialTheme.colorScheme.primary.copy(alpha = 0.1f)),
                contentAlignment = Alignment.Center
            ) {
                Icon(
                    imageVector = when (ride.status) {
                        RideStatus.ACCEPTED, RideStatus.DRIVER_ARRIVING -> Icons.Default.Navigation
                        RideStatus.ARRIVED -> Icons.Default.LocationOn
                        RideStatus.IN_PROGRESS -> Icons.Default.DirectionsCar
                        else -> Icons.Default.Info
                    },
                    contentDescription = null,
                    tint = MaterialTheme.colorScheme.primary,
                    modifier = Modifier.size(28.dp)
                )
            }
            
            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = when (ride.status) {
                        RideStatus.ACCEPTED, RideStatus.DRIVER_ARRIVING -> "Heading to Pickup"
                        RideStatus.ARRIVED -> "Arrived at Pickup"
                        RideStatus.IN_PROGRESS -> "Ride in Progress"
                        else -> "Unknown Status"
                    },
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold
                )
                Text(
                    text = when (ride.status) {
                        RideStatus.ACCEPTED, RideStatus.DRIVER_ARRIVING -> "Navigate to pickup location"
                        RideStatus.ARRIVED -> "Tap 'Start Ride' when rider is in"
                        RideStatus.IN_PROGRESS -> "Navigate to dropoff location"
                        else -> ""
                    },
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
        }
    }
}

@Composable
private fun NavigationCard(
    ride: Ride,
    context: Context,
    modifier: Modifier = Modifier
) {
    Card(modifier = modifier.fillMaxWidth()) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            Text(
                text = "Navigation",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold
            )
            
            // Pickup Location
            LocationRow(
                icon = Icons.Default.LocationOn,
                label = "Pickup",
                address = ride.pickupLocation.address ?: "Unknown location",
                iconColor = MaterialTheme.colorScheme.primary,
                onNavigate = if (ride.status != RideStatus.IN_PROGRESS) {
                    { NavigationHelper.startNavigation(context, ride.pickupLocation) }
                } else null
            )
            
            Divider()
            
            // Dropoff Location
            LocationRow(
                icon = Icons.Default.Place,
                label = "Dropoff",
                address = ride.dropoffLocation.address ?: "Unknown location",
                iconColor = MaterialTheme.colorScheme.secondary,
                onNavigate = if (ride.status == RideStatus.IN_PROGRESS) {
                    { NavigationHelper.startNavigation(context, ride.dropoffLocation) }
                } else null
            )
        }
    }
}

@Composable
private fun LocationRow(
    icon: androidx.compose.ui.graphics.vector.ImageVector,
    label: String,
    address: String,
    iconColor: androidx.compose.ui.graphics.Color,
    onNavigate: (() -> Unit)?,
    modifier: Modifier = Modifier
) {
    Row(
        modifier = modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.spacedBy(12.dp),
        verticalAlignment = Alignment.CenterVertically
    ) {
        Icon(
            imageVector = icon,
            contentDescription = label,
            tint = iconColor,
            modifier = Modifier.size(24.dp)
        )
        
        Column(modifier = Modifier.weight(1f)) {
            Text(
                text = label,
                style = MaterialTheme.typography.labelMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
            Text(
                text = address,
                style = MaterialTheme.typography.bodyMedium,
                fontWeight = FontWeight.Medium
            )
        }
        
        if (onNavigate != null) {
            IconButton(onClick = onNavigate) {
                Icon(
                    imageVector = Icons.Default.Navigation,
                    contentDescription = "Navigate",
                    tint = MaterialTheme.colorScheme.primary
                )
            }
        }
    }
}

@Composable
private fun RiderContactCard(
    ride: Ride,
    modifier: Modifier = Modifier
) {
    Card(modifier = modifier.fillMaxWidth()) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            Text(
                text = "Rider Contact",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold
            )
            
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                // Call Button
                OutlinedButton(
                    onClick = { /* TODO: Implement call functionality */ },
                    modifier = Modifier.weight(1f)
                ) {
                    Icon(
                        imageVector = Icons.Default.Phone,
                        contentDescription = "Call",
                        modifier = Modifier.size(20.dp)
                    )
                    Spacer(modifier = Modifier.width(8.dp))
                    Text("Call")
                }
                
                // Chat Button
                OutlinedButton(
                    onClick = { /* TODO: Navigate to chat */ },
                    modifier = Modifier.weight(1f)
                ) {
                    Icon(
                        imageVector = Icons.Default.Chat,
                        contentDescription = "Chat",
                        modifier = Modifier.size(20.dp)
                    )
                    Spacer(modifier = Modifier.width(8.dp))
                    Text("Chat")
                }
            }
        }
    }
}

@Composable
private fun RideActionButtons(
    ride: Ride,
    onStartRide: () -> Unit,
    onCompleteRide: () -> Unit,
    onCancelRide: () -> Unit,
    isLoading: Boolean,
    modifier: Modifier = Modifier
) {
    Column(
        modifier = modifier.fillMaxWidth(),
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        when (ride.status) {
            RideStatus.ARRIVED -> {
                Button(
                    onClick = onStartRide,
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(56.dp),
                    enabled = !isLoading
                ) {
                    Icon(
                        imageVector = Icons.Default.PlayArrow,
                        contentDescription = "Start Ride",
                        modifier = Modifier.size(24.dp)
                    )
                    Spacer(modifier = Modifier.width(8.dp))
                    Text(
                        text = "Start Ride",
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Bold
                    )
                }
            }
            RideStatus.IN_PROGRESS -> {
                Button(
                    onClick = onCompleteRide,
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(56.dp),
                    enabled = !isLoading,
                    colors = ButtonDefaults.buttonColors(
                        containerColor = MaterialTheme.colorScheme.tertiary
                    )
                ) {
                    Icon(
                        imageVector = Icons.Default.CheckCircle,
                        contentDescription = "Complete Ride",
                        modifier = Modifier.size(24.dp)
                    )
                    Spacer(modifier = Modifier.width(8.dp))
                    Text(
                        text = "Complete Ride",
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Bold
                    )
                }
            }
            else -> {
                // Show nothing for other statuses
            }
        }
        
        // Cancel Button (always available)
        OutlinedButton(
            onClick = onCancelRide,
            modifier = Modifier
                .fillMaxWidth()
                .height(48.dp),
            enabled = !isLoading,
            colors = ButtonDefaults.outlinedButtonColors(
                contentColor = MaterialTheme.colorScheme.error
            )
        ) {
            Icon(
                imageVector = Icons.Default.Cancel,
                contentDescription = "Cancel Ride",
                modifier = Modifier.size(20.dp)
            )
            Spacer(modifier = Modifier.width(8.dp))
            Text("Cancel Ride")
        }
    }
}

@Composable
private fun CancelRideDialog(
    onDismiss: () -> Unit,
    onConfirm: (String) -> Unit,
    modifier: Modifier = Modifier
) {
    var selectedReason by remember { mutableStateOf("") }
    val reasons = listOf(
        "Traffic issue",
        "Vehicle problem",
        "Emergency",
        "Rider not responding",
        "Wrong location",
        "Other"
    )
    
    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text("Cancel Ride") },
        text = {
            Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                Text("Please select a reason for cancellation:")
                
                reasons.forEach { reason ->
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .clip(RoundedCornerShape(8.dp))
                            .background(
                                if (selectedReason == reason) 
                                    MaterialTheme.colorScheme.primaryContainer 
                                else 
                                    MaterialTheme.colorScheme.surface
                            )
                            .padding(12.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        RadioButton(
                            selected = selectedReason == reason,
                            onClick = { selectedReason = reason }
                        )
                        Spacer(modifier = Modifier.width(8.dp))
                        Text(reason)
                    }
                }
            }
        },
        confirmButton = {
            Button(
                onClick = { onConfirm(selectedReason) },
                enabled = selectedReason.isNotEmpty()
            ) {
                Text("Confirm")
            }
        },
        dismissButton = {
            TextButton(onClick = onDismiss) {
                Text("Cancel")
            }
        }
    )
}
