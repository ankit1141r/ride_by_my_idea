package com.rideconnect.core.common.ui

import androidx.compose.animation.*
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
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import coil.compose.AsyncImage
import com.rideconnect.core.domain.model.*
import com.rideconnect.core.domain.viewmodel.RideState
import com.rideconnect.core.domain.viewmodel.RideViewModel

/**
 * Main ride request screen with location selection, fare estimate, and ride status.
 * 
 * Requirements: 3.1, 3.2, 3.3, 3.5
 */
@Composable
fun RideRequestScreen(
    viewModel: RideViewModel,
    onNavigateToLocationSearch: (isPickup: Boolean) -> Unit,
    onNavigateToTracking: () -> Unit,
    modifier: Modifier = Modifier
) {
    val rideState by viewModel.rideState.collectAsState()
    val activeRide by viewModel.activeRide.collectAsState()
    val fareEstimate by viewModel.fareEstimate.collectAsState()
    
    var pickupLocation by remember { mutableStateOf<Location?>(null) }
    var dropoffLocation by remember { mutableStateOf<Location?>(null) }
    var showCancelDialog by remember { mutableStateOf(false) }
    
    // Navigate to tracking when ride is accepted
    LaunchedEffect(rideState) {
        if (rideState is RideState.DriverAssigned || rideState is RideState.InProgress) {
            onNavigateToTracking()
        }
    }
    
    Box(modifier = modifier.fillMaxSize()) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(16.dp)
        ) {
            // Location selection section
            LocationSelectionCard(
                pickupLocation = pickupLocation,
                dropoffLocation = dropoffLocation,
                onPickupClick = { onNavigateToLocationSearch(true) },
                onDropoffClick = { onNavigateToLocationSearch(false) }
            )
            
            Spacer(modifier = Modifier.height(16.dp))
            
            // Fare estimate section
            AnimatedVisibility(
                visible = fareEstimate != null,
                enter = fadeIn() + expandVertically(),
                exit = fadeOut() + shrinkVertically()
            ) {
                fareEstimate?.let { estimate ->
                    FareEstimateCard(
                        fareEstimate = estimate,
                        onRequestRide = {
                            if (pickupLocation != null && dropoffLocation != null) {
                                viewModel.requestRide(pickupLocation!!, dropoffLocation!!)
                            }
                        },
                        isLoading = rideState is RideState.Loading
                    )
                }
            }
            
            Spacer(modifier = Modifier.height(16.dp))
            
            // Ride status section
            AnimatedVisibility(
                visible = rideState is RideState.Searching || activeRide != null,
                enter = fadeIn() + expandVertically(),
                exit = fadeOut() + shrinkVertically()
            ) {
                RideStatusCard(
                    rideState = rideState,
                    activeRide = activeRide,
                    onCancelRide = { showCancelDialog = true }
                )
            }
            
            // Error message
            if (rideState is RideState.Error) {
                Spacer(modifier = Modifier.height(16.dp))
                ErrorCard(message = (rideState as RideState.Error).message)
            }
        }
        
        // Calculate fare button
        if (pickupLocation != null && dropoffLocation != null && fareEstimate == null && rideState is RideState.Idle) {
            Button(
                onClick = {
                    viewModel.calculateFare(pickupLocation!!, dropoffLocation!!)
                },
                modifier = Modifier
                    .align(Alignment.BottomCenter)
                    .fillMaxWidth()
                    .padding(16.dp)
            ) {
                Text("Get Fare Estimate")
            }
        }
    }
    
    // Cancel ride dialog
    if (showCancelDialog) {
        CancelRideDialog(
            onDismiss = { showCancelDialog = false },
            onConfirm = { reason ->
                viewModel.cancelRide(reason)
                showCancelDialog = false
            }
        )
    }
}

@Composable
private fun LocationSelectionCard(
    pickupLocation: Location?,
    dropoffLocation: Location?,
    onPickupClick: () -> Unit,
    onDropoffClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier.fillMaxWidth(),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Column(
            modifier = Modifier.padding(16.dp)
        ) {
            // Pickup location
            LocationInputField(
                label = "Pickup Location",
                location = pickupLocation,
                icon = Icons.Default.LocationOn,
                iconTint = MaterialTheme.colorScheme.primary,
                onClick = onPickupClick
            )
            
            Spacer(modifier = Modifier.height(12.dp))
            
            // Dropoff location
            LocationInputField(
                label = "Dropoff Location",
                location = dropoffLocation,
                icon = Icons.Default.Place,
                iconTint = MaterialTheme.colorScheme.error,
                onClick = onDropoffClick
            )
        }
    }
}

@Composable
private fun LocationInputField(
    label: String,
    location: Location?,
    icon: androidx.compose.ui.graphics.vector.ImageVector,
    iconTint: Color,
    onClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    OutlinedButton(
        onClick = onClick,
        modifier = modifier.fillMaxWidth(),
        shape = RoundedCornerShape(8.dp)
    ) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Icon(
                imageVector = icon,
                contentDescription = null,
                tint = iconTint
            )
            Spacer(modifier = Modifier.width(12.dp))
            Column(
                modifier = Modifier.weight(1f)
            ) {
                Text(
                    text = label,
                    style = MaterialTheme.typography.labelSmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
                Text(
                    text = location?.address ?: "Select location",
                    style = MaterialTheme.typography.bodyMedium,
                    color = if (location != null) {
                        MaterialTheme.colorScheme.onSurface
                    } else {
                        MaterialTheme.colorScheme.onSurfaceVariant
                    }
                )
            }
        }
    }
}

@Composable
private fun FareEstimateCard(
    fareEstimate: FareEstimate,
    onRequestRide: () -> Unit,
    isLoading: Boolean,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier.fillMaxWidth(),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.primaryContainer
        )
    ) {
        Column(
            modifier = Modifier.padding(16.dp)
        ) {
            Text(
                text = "Fare Estimate",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold
            )
            
            Spacer(modifier = Modifier.height(12.dp))
            
            // Fare breakdown
            FareBreakdownRow("Base Fare", fareEstimate.baseFare)
            FareBreakdownRow("Distance (${String.format("%.1f", fareEstimate.distance)} km)", fareEstimate.distanceFare)
            FareBreakdownRow("Time (~${fareEstimate.estimatedDuration} min)", fareEstimate.timeFare)
            
            Divider(modifier = Modifier.padding(vertical = 8.dp))
            
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = "Total",
                    style = MaterialTheme.typography.titleLarge,
                    fontWeight = FontWeight.Bold
                )
                Text(
                    text = "₹${String.format("%.2f", fareEstimate.totalFare)}",
                    style = MaterialTheme.typography.titleLarge,
                    fontWeight = FontWeight.Bold,
                    color = MaterialTheme.colorScheme.primary
                )
            }
            
            Spacer(modifier = Modifier.height(16.dp))
            
            Button(
                onClick = onRequestRide,
                modifier = Modifier.fillMaxWidth(),
                enabled = !isLoading
            ) {
                if (isLoading) {
                    CircularProgressIndicator(
                        modifier = Modifier.size(20.dp),
                        color = MaterialTheme.colorScheme.onPrimary
                    )
                } else {
                    Text("Request Ride")
                }
            }
        }
    }
}

@Composable
private fun FareBreakdownRow(
    label: String,
    amount: Double,
    modifier: Modifier = Modifier
) {
    Row(
        modifier = modifier
            .fillMaxWidth()
            .padding(vertical = 4.dp),
        horizontalArrangement = Arrangement.SpaceBetween
    ) {
        Text(
            text = label,
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
        Text(
            text = "₹${String.format("%.2f", amount)}",
            style = MaterialTheme.typography.bodyMedium
        )
    }
}

@Composable
private fun RideStatusCard(
    rideState: RideState,
    activeRide: Ride?,
    onCancelRide: () -> Unit,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier.fillMaxWidth(),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Column(
            modifier = Modifier.padding(16.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            when (rideState) {
                is RideState.Searching -> {
                    CircularProgressIndicator()
                    Spacer(modifier = Modifier.height(16.dp))
                    Text(
                        text = "Searching for drivers...",
                        style = MaterialTheme.typography.titleMedium
                    )
                    Text(
                        text = "This may take a few moments",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
                is RideState.DriverAssigned -> {
                    activeRide?.driverDetails?.let { driver ->
                        DriverDetailsSection(driver)
                    }
                }
                else -> {}
            }
            
            // Cancel button
            if (rideState is RideState.Searching || rideState is RideState.DriverAssigned) {
                Spacer(modifier = Modifier.height(16.dp))
                OutlinedButton(
                    onClick = onCancelRide,
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Text("Cancel Ride")
                }
            }
        }
    }
}

@Composable
private fun DriverDetailsSection(
    driver: DriverDetails,
    modifier: Modifier = Modifier
) {
    Column(
        modifier = modifier.fillMaxWidth(),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        // Driver photo
        AsyncImage(
            model = driver.profilePhotoUrl,
            contentDescription = "Driver photo",
            modifier = Modifier
                .size(80.dp)
                .clip(CircleShape)
                .background(MaterialTheme.colorScheme.surfaceVariant)
        )
        
        Spacer(modifier = Modifier.height(12.dp))
        
        // Driver name
        Text(
            text = driver.name,
            style = MaterialTheme.typography.titleLarge,
            fontWeight = FontWeight.Bold
        )
        
        // Driver rating
        Row(
            verticalAlignment = Alignment.CenterVertically
        ) {
            Icon(
                imageVector = Icons.Default.Star,
                contentDescription = null,
                tint = Color(0xFFFFC107),
                modifier = Modifier.size(20.dp)
            )
            Spacer(modifier = Modifier.width(4.dp))
            Text(
                text = String.format("%.1f", driver.rating),
                style = MaterialTheme.typography.bodyMedium
            )
        }
        
        Spacer(modifier = Modifier.height(8.dp))
        
        // Vehicle details
        driver.vehicleDetails?.let { vehicle ->
            Text(
                text = "${vehicle.color} ${vehicle.make} ${vehicle.model}",
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
            Text(
                text = vehicle.licensePlate,
                style = MaterialTheme.typography.bodyLarge,
                fontWeight = FontWeight.Bold
            )
        }
        
        Spacer(modifier = Modifier.height(16.dp))
        
        // Status message
        Card(
            modifier = Modifier.fillMaxWidth(),
            colors = CardDefaults.cardColors(
                containerColor = MaterialTheme.colorScheme.secondaryContainer
            )
        ) {
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(12.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                Icon(
                    imageVector = Icons.Default.Info,
                    contentDescription = null,
                    tint = MaterialTheme.colorScheme.onSecondaryContainer
                )
                Spacer(modifier = Modifier.width(8.dp))
                Text(
                    text = "Driver is on the way to your location",
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSecondaryContainer
                )
            }
        }
    }
}

@Composable
private fun ErrorCard(
    message: String,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.errorContainer
        )
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Icon(
                imageVector = Icons.Default.Warning,
                contentDescription = null,
                tint = MaterialTheme.colorScheme.onErrorContainer
            )
            Spacer(modifier = Modifier.width(12.dp))
            Text(
                text = message,
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onErrorContainer
            )
        }
    }
}

@Composable
private fun CancelRideDialog(
    onDismiss: () -> Unit,
    onConfirm: (String) -> Unit
) {
    var selectedReason by remember { mutableStateOf("Changed my mind") }
    val reasons = listOf(
        "Changed my mind",
        "Driver is taking too long",
        "Found alternative transport",
        "Wrong pickup location",
        "Other"
    )
    
    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text("Cancel Ride") },
        text = {
            Column {
                Text("Please select a reason for cancellation:")
                Spacer(modifier = Modifier.height(8.dp))
                reasons.forEach { reason ->
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(vertical = 4.dp),
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
            Button(onClick = { onConfirm(selectedReason) }) {
                Text("Confirm")
            }
        },
        dismissButton = {
            TextButton(onClick = onDismiss) {
                Text("Keep Ride")
            }
        }
    )
}
