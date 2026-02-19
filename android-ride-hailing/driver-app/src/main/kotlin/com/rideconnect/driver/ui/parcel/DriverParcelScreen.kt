package com.rideconnect.driver.ui.parcel

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
import com.rideconnect.core.domain.viewmodel.DriverViewModel

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun DriverParcelScreen(
    viewModel: DriverViewModel,
    parcel: ParcelDelivery,
    onNavigateToMap: () -> Unit,
    onCallContact: (String) -> Unit,
    modifier: Modifier = Modifier
) {
    val uiState by viewModel.uiState.collectAsState()
    
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Parcel Delivery") },
                actions = {
                    IconButton(onClick = onNavigateToMap) {
                        Icon(Icons.Default.Map, contentDescription = "View Map")
                    }
                }
            )
        }
    ) { paddingValues ->
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
            
            // Parcel Details
            ParcelDetailsCard(parcel = parcel)
            
            // Current Location Card
            when (parcel.status) {
                ParcelStatus.ACCEPTED -> {
                    LocationCard(
                        title = "Pickup Location",
                        location = parcel.pickupLocation,
                        contactName = parcel.senderName,
                        contactPhone = parcel.senderPhone,
                        onCall = onCallContact
                    )
                    
                    Button(
                        onClick = { viewModel.confirmPickup(parcel.id) },
                        modifier = Modifier
                            .fillMaxWidth()
                            .height(56.dp),
                        enabled = !uiState.isLoading
                    ) {
                        if (uiState.isLoading) {
                            CircularProgressIndicator(
                                modifier = Modifier.size(24.dp),
                                color = MaterialTheme.colorScheme.onPrimary
                            )
                        } else {
                            Icon(Icons.Default.CheckCircle, contentDescription = null)
                            Spacer(modifier = Modifier.width(8.dp))
                            Text("Confirm Pickup")
                        }
                    }
                }
                
                ParcelStatus.PICKED_UP, ParcelStatus.IN_TRANSIT -> {
                    LocationCard(
                        title = "Delivery Location",
                        location = parcel.dropoffLocation,
                        contactName = parcel.recipientName,
                        contactPhone = parcel.recipientPhone,
                        onCall = onCallContact
                    )
                    
                    Button(
                        onClick = { viewModel.confirmDelivery(parcel.id) },
                        modifier = Modifier
                            .fillMaxWidth()
                            .height(56.dp),
                        enabled = !uiState.isLoading
                    ) {
                        if (uiState.isLoading) {
                            CircularProgressIndicator(
                                modifier = Modifier.size(24.dp),
                                color = MaterialTheme.colorScheme.onPrimary
                            )
                        } else {
                            Icon(Icons.Default.Done, contentDescription = null)
                            Spacer(modifier = Modifier.width(8.dp))
                            Text("Confirm Delivery")
                        }
                    }
                }
                
                else -> {
                    // Show both locations for reference
                    LocationCard(
                        title = "Pickup Location",
                        location = parcel.pickupLocation,
                        contactName = parcel.senderName,
                        contactPhone = parcel.senderPhone,
                        onCall = onCallContact
                    )
                    
                    LocationCard(
                        title = "Delivery Location",
                        location = parcel.dropoffLocation,
                        contactName = parcel.recipientName,
                        contactPhone = parcel.recipientPhone,
                        onCall = onCallContact
                    )
                }
            }
            
            // Error Message
            if (uiState.error != null) {
                Card(
                    colors = CardDefaults.cardColors(
                        containerColor = MaterialTheme.colorScheme.errorContainer
                    ),
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Row(
                        modifier = Modifier.padding(16.dp),
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
                            color = MaterialTheme.colorScheme.onErrorContainer
                        )
                    }
                }
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
        ParcelStatus.REQUESTED -> Triple("New Request", MaterialTheme.colorScheme.primary, Icons.Default.Schedule)
        ParcelStatus.ACCEPTED -> Triple("Heading to Pickup", MaterialTheme.colorScheme.tertiary, Icons.Default.DirectionsCar)
        ParcelStatus.PICKED_UP -> Triple("Parcel Picked Up", MaterialTheme.colorScheme.secondary, Icons.Default.LocalShipping)
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
                    text = "Delivery Instructions",
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
private fun LocationCard(
    title: String,
    location: com.rideconnect.core.domain.model.Location,
    contactName: String,
    contactPhone: String,
    onCall: (String) -> Unit,
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
                text = title,
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold
            )
            
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                Icon(
                    imageVector = Icons.Default.LocationOn,
                    contentDescription = null,
                    tint = MaterialTheme.colorScheme.primary
                )
                
                Column(modifier = Modifier.weight(1f)) {
                    Text(
                        text = location.address ?: "Unknown location",
                        style = MaterialTheme.typography.bodyLarge,
                        fontWeight = FontWeight.Medium
                    )
                }
            }
            
            Divider()
            
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Column {
                    Text(
                        text = "Contact",
                        style = MaterialTheme.typography.labelMedium,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                    Text(
                        text = contactName,
                        style = MaterialTheme.typography.bodyLarge,
                        fontWeight = FontWeight.Medium
                    )
                    Text(
                        text = contactPhone,
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
                
                IconButton(
                    onClick = { onCall(contactPhone) }
                ) {
                    Icon(
                        imageVector = Icons.Default.Phone,
                        contentDescription = "Call Contact",
                        tint = MaterialTheme.colorScheme.primary
                    )
                }
            }
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
