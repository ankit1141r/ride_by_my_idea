package com.rideconnect.core.common.ui

import androidx.compose.animation.*
import androidx.compose.animation.core.*
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
import com.google.android.gms.maps.model.BitmapDescriptorFactory
import com.google.android.gms.maps.model.LatLng
import com.google.maps.android.compose.*
import com.rideconnect.core.common.map.*
import com.rideconnect.core.domain.model.*
import com.rideconnect.core.domain.viewmodel.RideState
import com.rideconnect.core.domain.viewmodel.RideViewModel
import kotlinx.coroutines.delay

/**
 * Real-time ride tracking screen with driver location updates and route display.
 * 
 * Requirements: 6.1, 6.2, 6.3, 6.4, 6.6, 6.8
 */
@Composable
fun RideTrackingScreen(
    viewModel: RideViewModel,
    onNavigateBack: () -> Unit,
    modifier: Modifier = Modifier
) {
    val rideState by viewModel.rideState.collectAsState()
    val activeRide by viewModel.activeRide.collectAsState()
    val driverLocation by viewModel.driverLocation.collectAsState()
    
    var showCancelDialog by remember { mutableStateOf(false) }
    var estimatedArrivalTime by remember { mutableStateOf(0) }
    
    // Calculate ETA based on driver location
    LaunchedEffect(driverLocation, activeRide) {
        if (driverLocation != null && activeRide != null) {
            // Simplified ETA calculation (in real app, use Google Directions API)
            val distance = calculateDistance(
                driverLocation!!,
                if (activeRide!!.status == RideStatus.IN_PROGRESS) {
                    activeRide!!.dropoffLocation
                } else {
                    activeRide!!.pickupLocation
                }
            )
            estimatedArrivalTime = (distance / 0.5).toInt() // Assuming 30 km/h average speed
        }
    }
    
    Box(modifier = modifier.fillMaxSize()) {
        // Map with driver and destination markers
        RideTrackingMap(
            activeRide = activeRide,
            driverLocation = driverLocation,
            modifier = Modifier.fillMaxSize()
        )
        
        // Top bar with back button
        TopAppBar(
            title = { Text("Track Ride") },
            navigationIcon = {
                IconButton(onClick = onNavigateBack) {
                    Icon(Icons.Default.ArrowBack, contentDescription = "Back")
                }
            },
            colors = TopAppBarDefaults.topAppBarColors(
                containerColor = Color.Transparent
            ),
            modifier = Modifier
                .fillMaxWidth()
                .background(
                    MaterialTheme.colorScheme.surface.copy(alpha = 0.9f),
                    RoundedCornerShape(bottomStart = 16.dp, bottomEnd = 16.dp)
                )
        )
        
        // Bottom sheet with ride details
        Column(
            modifier = Modifier
                .align(Alignment.BottomCenter)
                .fillMaxWidth()
        ) {
            activeRide?.let { ride ->
                RideDetailsBottomSheet(
                    ride = ride,
                    rideState = rideState,
                    driverLocation = driverLocation,
                    estimatedArrivalTime = estimatedArrivalTime,
                    onCancelRide = { showCancelDialog = true }
                )
            }
        }
        
        // Connection status indicator
        if (driverLocation == null && activeRide != null) {
            Card(
                modifier = Modifier
                    .align(Alignment.TopCenter)
                    .padding(top = 80.dp)
                    .padding(horizontal = 16.dp),
                colors = CardDefaults.cardColors(
                    containerColor = MaterialTheme.colorScheme.errorContainer
                )
            ) {
                Row(
                    modifier = Modifier.padding(12.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Icon(
                        imageVector = Icons.Default.Warning,
                        contentDescription = null,
                        tint = MaterialTheme.colorScheme.onErrorContainer
                    )
                    Spacer(modifier = Modifier.width(8.dp))
                    Text(
                        text = "Waiting for driver location updates...",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onErrorContainer
                    )
                }
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
                onNavigateBack()
            }
        )
    }
}

@Composable
private fun RideTrackingMap(
    activeRide: Ride?,
    driverLocation: Location?,
    modifier: Modifier = Modifier
) {
    val cameraPositionState = rememberCameraPositionState()
    
    // Animate camera to show both driver and destination
    LaunchedEffect(driverLocation, activeRide) {
        if (driverLocation != null && activeRide != null) {
            val destination = if (activeRide.status == RideStatus.IN_PROGRESS) {
                activeRide.dropoffLocation
            } else {
                activeRide.pickupLocation
            }
            
            // Adjust camera to show both markers
            adjustCameraBounds(
                cameraPositionState,
                listOf(driverLocation.toLatLng(), destination.toLatLng())
            )
        }
    }
    
    RideConnectMap(
        modifier = modifier,
        cameraPositionState = cameraPositionState,
        uiSettings = rememberRideConnectMapUiSettings(),
        properties = rememberRideConnectMapProperties(showTraffic = true)
    ) {
        // Driver marker with animation
        driverLocation?.let { location ->
            AnimatedDriverMarker(
                position = location.toLatLng(),
                title = "Driver"
            )
        }
        
        // Destination marker
        activeRide?.let { ride ->
            val destination = if (ride.status == RideStatus.IN_PROGRESS) {
                ride.dropoffLocation
            } else {
                ride.pickupLocation
            }
            
            Marker(
                state = MarkerState(position = destination.toLatLng()),
                title = if (ride.status == RideStatus.IN_PROGRESS) "Dropoff" else "Pickup",
                icon = BitmapDescriptorFactory.defaultMarker(
                    if (ride.status == RideStatus.IN_PROGRESS) {
                        BitmapDescriptorFactory.HUE_RED
                    } else {
                        BitmapDescriptorFactory.HUE_GREEN
                    }
                )
            )
        }
        
        // Route polyline (simplified - in real app, use Google Directions API)
        if (driverLocation != null && activeRide != null) {
            val destination = if (activeRide.status == RideStatus.IN_PROGRESS) {
                activeRide.dropoffLocation
            } else {
                activeRide.pickupLocation
            }
            
            Polyline(
                points = listOf(
                    driverLocation.toLatLng(),
                    destination.toLatLng()
                ),
                color = MaterialTheme.colorScheme.primary,
                width = 10f
            )
        }
    }
}

@Composable
private fun AnimatedDriverMarker(
    position: LatLng,
    title: String,
    modifier: Modifier = Modifier
) {
    // Smooth marker animation
    val animatedPosition by animateLatLngAsState(
        targetValue = position,
        animationSpec = tween(durationMillis = 1000, easing = LinearEasing)
    )
    
    Marker(
        state = MarkerState(position = animatedPosition),
        title = title,
        icon = BitmapDescriptorFactory.defaultMarker(BitmapDescriptorFactory.HUE_BLUE)
    )
}

@Composable
private fun animateLatLngAsState(
    targetValue: LatLng,
    animationSpec: AnimationSpec<Float> = spring()
): State<LatLng> {
    val latitude by animateFloatAsState(
        targetValue = targetValue.latitude.toFloat(),
        animationSpec = animationSpec,
        label = "latitude"
    )
    val longitude by animateFloatAsState(
        targetValue = targetValue.longitude.toFloat(),
        animationSpec = animationSpec,
        label = "longitude"
    )
    
    return remember {
        derivedStateOf {
            LatLng(latitude.toDouble(), longitude.toDouble())
        }
    }
}

@Composable
private fun RideDetailsBottomSheet(
    ride: Ride,
    rideState: RideState,
    driverLocation: Location?,
    estimatedArrivalTime: Int,
    onCancelRide: () -> Unit,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier
            .fillMaxWidth(),
        shape = RoundedCornerShape(topStart = 24.dp, topEnd = 24.dp),
        elevation = CardDefaults.cardElevation(defaultElevation = 8.dp)
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(20.dp)
        ) {
            // Status indicator
            RideStatusIndicator(rideState = rideState)
            
            Spacer(modifier = Modifier.height(16.dp))
            
            // ETA display
            if (driverLocation != null && estimatedArrivalTime > 0) {
                ETACard(estimatedMinutes = estimatedArrivalTime)
                Spacer(modifier = Modifier.height(16.dp))
            }
            
            // Driver details
            ride.driverDetails?.let { driver ->
                DriverInfoRow(driver = driver)
                Spacer(modifier = Modifier.height(16.dp))
            }
            
            // Destination info
            DestinationInfoCard(
                ride = ride,
                isInProgress = ride.status == RideStatus.IN_PROGRESS
            )
            
            Spacer(modifier = Modifier.height(16.dp))
            
            // Action buttons
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                // Call driver button
                ride.driverDetails?.let {
                    OutlinedButton(
                        onClick = { /* Handle call */ },
                        modifier = Modifier.weight(1f)
                    ) {
                        Icon(Icons.Default.Call, contentDescription = null)
                        Spacer(modifier = Modifier.width(8.dp))
                        Text("Call")
                    }
                }
                
                // Chat button
                OutlinedButton(
                    onClick = { /* Handle chat */ },
                    modifier = Modifier.weight(1f)
                ) {
                    Icon(Icons.Default.Chat, contentDescription = null)
                    Spacer(modifier = Modifier.width(8.dp))
                    Text("Chat")
                }
            }
            
            // Cancel button (only if not in progress)
            if (ride.status != RideStatus.IN_PROGRESS) {
                Spacer(modifier = Modifier.height(12.dp))
                OutlinedButton(
                    onClick = onCancelRide,
                    modifier = Modifier.fillMaxWidth(),
                    colors = ButtonDefaults.outlinedButtonColors(
                        contentColor = MaterialTheme.colorScheme.error
                    )
                ) {
                    Text("Cancel Ride")
                }
            }
        }
    }
}

@Composable
private fun RideStatusIndicator(
    rideState: RideState,
    modifier: Modifier = Modifier
) {
    val (statusText, statusColor) = when (rideState) {
        is RideState.DriverAssigned -> "Driver Assigned" to MaterialTheme.colorScheme.primary
        is RideState.DriverArrived -> "Driver Arrived" to MaterialTheme.colorScheme.tertiary
        is RideState.InProgress -> "Ride in Progress" to MaterialTheme.colorScheme.secondary
        else -> "Tracking Ride" to MaterialTheme.colorScheme.onSurfaceVariant
    }
    
    Row(
        modifier = modifier.fillMaxWidth(),
        verticalAlignment = Alignment.CenterVertically
    ) {
        Box(
            modifier = Modifier
                .size(12.dp)
                .clip(CircleShape)
                .background(statusColor)
        )
        Spacer(modifier = Modifier.width(8.dp))
        Text(
            text = statusText,
            style = MaterialTheme.typography.titleMedium,
            fontWeight = FontWeight.Bold,
            color = statusColor
        )
    }
}

@Composable
private fun ETACard(
    estimatedMinutes: Int,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.primaryContainer
        )
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.SpaceBetween
        ) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Icon(
                    imageVector = Icons.Default.Schedule,
                    contentDescription = null,
                    tint = MaterialTheme.colorScheme.onPrimaryContainer
                )
                Spacer(modifier = Modifier.width(8.dp))
                Text(
                    text = "Estimated Arrival",
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onPrimaryContainer
                )
            }
            Text(
                text = "$estimatedMinutes min",
                style = MaterialTheme.typography.titleLarge,
                fontWeight = FontWeight.Bold,
                color = MaterialTheme.colorScheme.onPrimaryContainer
            )
        }
    }
}

@Composable
private fun DriverInfoRow(
    driver: DriverDetails,
    modifier: Modifier = Modifier
) {
    Row(
        modifier = modifier.fillMaxWidth(),
        verticalAlignment = Alignment.CenterVertically
    ) {
        // Driver photo
        AsyncImage(
            model = driver.profilePhotoUrl,
            contentDescription = "Driver photo",
            modifier = Modifier
                .size(56.dp)
                .clip(CircleShape)
                .background(MaterialTheme.colorScheme.surfaceVariant)
        )
        
        Spacer(modifier = Modifier.width(12.dp))
        
        Column(modifier = Modifier.weight(1f)) {
            Text(
                text = driver.name,
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold
            )
            
            Row(verticalAlignment = Alignment.CenterVertically) {
                Icon(
                    imageVector = Icons.Default.Star,
                    contentDescription = null,
                    tint = Color(0xFFFFC107),
                    modifier = Modifier.size(16.dp)
                )
                Spacer(modifier = Modifier.width(4.dp))
                Text(
                    text = String.format("%.1f", driver.rating),
                    style = MaterialTheme.typography.bodySmall
                )
            }
            
            driver.vehicleDetails?.let { vehicle ->
                Text(
                    text = "${vehicle.color} ${vehicle.make} • ${vehicle.licensePlate}",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
        }
    }
}

@Composable
private fun DestinationInfoCard(
    ride: Ride,
    isInProgress: Boolean,
    modifier: Modifier = Modifier
) {
    val destination = if (isInProgress) ride.dropoffLocation else ride.pickupLocation
    val label = if (isInProgress) "Dropoff Location" else "Pickup Location"
    
    Card(
        modifier = modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surfaceVariant
        )
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(12.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Icon(
                imageVector = if (isInProgress) Icons.Default.Place else Icons.Default.LocationOn,
                contentDescription = null,
                tint = if (isInProgress) {
                    MaterialTheme.colorScheme.error
                } else {
                    MaterialTheme.colorScheme.primary
                }
            )
            Spacer(modifier = Modifier.width(12.dp))
            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = label,
                    style = MaterialTheme.typography.labelSmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
                Text(
                    text = destination.address ?: "Location",
                    style = MaterialTheme.typography.bodyMedium,
                    fontWeight = FontWeight.Medium
                )
            }
        }
    }
}

// Helper function to calculate distance between two locations (simplified)
private fun calculateDistance(from: Location, to: Location): Double {
    val earthRadius = 6371.0 // km
    val dLat = Math.toRadians(to.latitude - from.latitude)
    val dLon = Math.toRadians(to.longitude - from.longitude)
    val a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
            Math.cos(Math.toRadians(from.latitude)) * Math.cos(Math.toRadians(to.latitude)) *
            Math.sin(dLon / 2) * Math.sin(dLon / 2)
    val c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))
    return earthRadius * c
}
