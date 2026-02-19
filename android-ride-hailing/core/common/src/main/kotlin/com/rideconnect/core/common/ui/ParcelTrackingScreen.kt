package com.rideconnect.core.common.ui

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.rideconnect.core.domain.model.ParcelDelivery
import com.rideconnect.core.domain.model.ParcelStatus
import com.rideconnect.core.domain.viewmodel.ParcelViewModel
import java.time.format.DateTimeFormatter

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ParcelTrackingScreen(
    viewModel: ParcelViewModel,
    parcelId: String,
    onNavigateBack: () -> Unit,
    onCallDriver: (String) -> Unit,
    modifier: Modifier = Modifier
) {
    val parcelHistory by viewModel.parcelHistory.collectAsState()
    val parcel = remember(parcelHistory, parcelId) {
        parcelHistory.find { it.id == parcelId }
    }
    
    LaunchedEffect(parcelId) {
        viewModel.loadParcelHistory()
    }
    
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Track Parcel") },
                navigationIcon = {
                    IconButton(onClick = onNavigateBack) {
                        Icon(Icons.Default.ArrowBack, contentDescription = "Back")
                    }
                }
            )
        }
    ) { paddingValues ->
        if (parcel == null) {
            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(paddingValues),
                contentAlignment = Alignment.Center
            ) {
                CircularProgressIndicator()
            }
        } else {
            Column(
                modifier = modifier
                    .fillMaxSize()
                    .padding(paddingValues)
                    .verticalScroll(rememberScrollState())
                    .padding(16.dp),
                verticalArrangement = Arrangement.spacedBy(16.dp)
            ) {
                // Status Card
                ParcelStatusCard(parcel = parcel)
                
                // Driver Information (if assigned)
                if (parcel.driverId != null) {
                    DriverInfoCard(
                        driverId = parcel.driverId,
                        onCallDriver = onCallDriver
                    )
                }
                
                // Parcel Details
                ParcelDetailsCard(parcel = parcel)
                
                // Location Information
                LocationInfoCard(parcel = parcel)
                
                // Timeline
                ParcelTimelineCard(parcel = parcel)
            }
        }
    }
}

@Composable
private fun ParcelStatusCard(
    parcel: ParcelDelivery,
    modifier: Modifier = Modifier
) {
    val (statusText, statusColor, statusIcon) = when (parcel.status) {
        ParcelStatus.REQUESTED -> Triple("Requested", MaterialTheme.colorScheme.primary, Icons.Default.Schedule)
        ParcelStatus.ACCEPTED -> Triple("Driver Assigned", MaterialTheme.colorScheme.tertiary, Icons.Default.CheckCircle)
        ParcelStatus.PICKED_UP -> Triple("Picked Up", MaterialTheme.colorScheme.secondary, Icons.Default.LocalShipping)
        ParcelStatus.IN_TRANSIT -> Triple("In Transit", MaterialTheme.colorScheme.secondary, Icons.Default.LocalShipping)
        ParcelStatus.DELIVERED -> Triple("Delivered", MaterialTheme.colorScheme.tertiary, Icons.Default.Done)
        ParcelStatus.CANCELLED -> Triple("Cancelled", MaterialTheme.colorScheme.error, Icons.Default.Cancel)
    }
    
    Card(
        modifier = modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = statusColor.copy(alpha = 0.1f)
        )
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(20.dp),
            horizontalArrangement = Arrangement.spacedBy(16.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Icon(
                imageVector = statusIcon,
                contentDescription = null,
                modifier = Modifier.size(48.dp),
                tint = statusColor
            )
            
            Column {
                Text(
                    text = "Status",
                    style = MaterialTheme.typography.labelMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
                Text(
                    text = statusText,
                    style = MaterialTheme.typography.headlineSmall,
                    fontWeight = FontWeight.Bold,
                    color = statusColor
                )
            }
        }
    }
}

@Composable
private fun DriverInfoCard(
    driverId: String,
    onCallDriver: (String) -> Unit,
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
                text = "Driver Information",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold
            )
            
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Row(
                    horizontalArrangement = Arrangement.spacedBy(12.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Icon(
                        imageVector = Icons.Default.Person,
                        contentDescription = null,
                        modifier = Modifier.size(40.dp),
                        tint = MaterialTheme.colorScheme.primary
                    )
                    
                    Column {
                        Text(
                            text = "Driver ID: $driverId",
                            style = MaterialTheme.typography.bodyLarge,
                            fontWeight = FontWeight.Medium
                        )
                        Text(
                            text = "On the way",
                            style = MaterialTheme.typography.bodyMedium,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }
                }
                
                IconButton(
                    onClick = { onCallDriver(driverId) }
                ) {
                    Icon(
                        imageVector = Icons.Default.Phone,
                        contentDescription = "Call Driver",
                        tint = MaterialTheme.colorScheme.primary
                    )
                }
            }
        }
    }
}

@Composable
private fun ParcelDetailsCard(
    parcel: ParcelDelivery,
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
                text = "Parcel Details",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold
            )
            
            DetailRow(
                label = "Size",
                value = parcel.parcelSize.name.lowercase().replaceFirstChar { it.uppercase() }
            )
            
            if (parcel.fare != null) {
                DetailRow(
                    label = "Fare",
                    value = "₹${parcel.fare}"
                )
            }
            
            if (parcel.instructions != null) {
                Divider(modifier = Modifier.padding(vertical = 4.dp))
                Text(
                    text = "Instructions",
                    style = MaterialTheme.typography.labelMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
                Text(
                    text = parcel.instructions,
                    style = MaterialTheme.typography.bodyMedium
                )
            }
        }
    }
}

@Composable
private fun LocationInfoCard(
    parcel: ParcelDelivery,
    modifier: Modifier = Modifier
) {
    Card(modifier = modifier.fillMaxWidth()) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            Text(
                text = "Locations",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold
            )
            
            // Pickup Location
            LocationItem(
                icon = Icons.Default.LocationOn,
                label = "Pickup",
                address = parcel.pickupLocation.address ?: "Unknown",
                contactName = parcel.senderName,
                contactPhone = parcel.senderPhone
            )
            
            Divider()
            
            // Dropoff Location
            LocationItem(
                icon = Icons.Default.Place,
                label = "Dropoff",
                address = parcel.dropoffLocation.address ?: "Unknown",
                contactName = parcel.recipientName,
                contactPhone = parcel.recipientPhone
            )
        }
    }
}

@Composable
private fun LocationItem(
    icon: androidx.compose.ui.graphics.vector.ImageVector,
    label: String,
    address: String,
    contactName: String,
    contactPhone: String,
    modifier: Modifier = Modifier
) {
    Row(
        modifier = modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        Icon(
            imageVector = icon,
            contentDescription = null,
            tint = MaterialTheme.colorScheme.primary
        )
        
        Column(modifier = Modifier.weight(1f)) {
            Text(
                text = label,
                style = MaterialTheme.typography.labelMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
            Text(
                text = address,
                style = MaterialTheme.typography.bodyLarge,
                fontWeight = FontWeight.Medium
            )
            Spacer(modifier = Modifier.height(4.dp))
            Text(
                text = "$contactName • $contactPhone",
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }
    }
}

@Composable
private fun ParcelTimelineCard(
    parcel: ParcelDelivery,
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
                text = "Timeline",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold
            )
            
            val timeFormatter = DateTimeFormatter.ofPattern("MMM dd, yyyy HH:mm")
            
            TimelineItem(
                label = "Requested",
                time = parcel.requestedAt.format(timeFormatter),
                isCompleted = true
            )
            
            if (parcel.pickedUpAt != null) {
                TimelineItem(
                    label = "Picked Up",
                    time = parcel.pickedUpAt.format(timeFormatter),
                    isCompleted = true
                )
            }
            
            if (parcel.deliveredAt != null) {
                TimelineItem(
                    label = "Delivered",
                    time = parcel.deliveredAt.format(timeFormatter),
                    isCompleted = true,
                    isLast = true
                )
            }
        }
    }
}

@Composable
private fun TimelineItem(
    label: String,
    time: String,
    isCompleted: Boolean,
    isLast: Boolean = false,
    modifier: Modifier = Modifier
) {
    Row(
        modifier = modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        Column(
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Icon(
                imageVector = if (isCompleted) Icons.Default.CheckCircle else Icons.Default.Circle,
                contentDescription = null,
                tint = if (isCompleted) {
                    MaterialTheme.colorScheme.primary
                } else {
                    MaterialTheme.colorScheme.onSurfaceVariant
                },
                modifier = Modifier.size(24.dp)
            )
            
            if (!isLast) {
                Divider(
                    modifier = Modifier
                        .width(2.dp)
                        .height(32.dp),
                    color = if (isCompleted) {
                        MaterialTheme.colorScheme.primary
                    } else {
                        MaterialTheme.colorScheme.onSurfaceVariant
                    }
                )
            }
        }
        
        Column(modifier = Modifier.weight(1f)) {
            Text(
                text = label,
                style = MaterialTheme.typography.bodyLarge,
                fontWeight = if (isCompleted) FontWeight.Bold else FontWeight.Normal
            )
            Text(
                text = time,
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }
    }
}

@Composable
private fun DetailRow(
    label: String,
    value: String,
    modifier: Modifier = Modifier
) {
    Row(
        modifier = modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.SpaceBetween
    ) {
        Text(
            text = label,
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
        Text(
            text = value,
            style = MaterialTheme.typography.bodyMedium,
            fontWeight = FontWeight.Medium
        )
    }
}
