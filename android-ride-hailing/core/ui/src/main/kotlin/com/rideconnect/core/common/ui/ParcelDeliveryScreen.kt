@file:OptIn(ExperimentalMaterial3Api::class)

package com.rideconnect.core.common.ui

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.selection.selectable
import androidx.compose.foundation.selection.selectableGroup
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.semantics.Role
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.rideconnect.core.domain.model.Location
import com.rideconnect.core.domain.model.ParcelSize
import com.rideconnect.core.domain.viewmodel.ParcelViewModel

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ParcelDeliveryScreen(
    viewModel: ParcelViewModel,
    onNavigateToLocationPicker: (isPickup: Boolean) -> Unit,
    onNavigateBack: () -> Unit,
    modifier: Modifier = Modifier
) {
    val isLoading by viewModel.isLoading.collectAsState()
    val error by viewModel.error.collectAsState()
    val requestSuccess by viewModel.requestSuccess.collectAsState()
    val activeParcel by viewModel.activeParcel.collectAsState()
    
    var selectedSize by remember { mutableStateOf<ParcelSize?>(null) }
    var senderName by remember { mutableStateOf("") }
    var senderPhone by remember { mutableStateOf("") }
    var recipientName by remember { mutableStateOf("") }
    var recipientPhone by remember { mutableStateOf("") }
    var instructions by remember { mutableStateOf("") }
    var pickupLocation by remember { mutableStateOf<Location?>(null) }
    var dropoffLocation by remember { mutableStateOf<Location?>(null) }
    
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Parcel Delivery") },
                navigationIcon = {
                    IconButton(onClick = onNavigateBack) {
                        Icon(Icons.Default.ArrowBack, contentDescription = "Back")
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
            // Parcel Size Selection
            Text(
                text = "Select Parcel Size",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold
            )
            
            ParcelSizeSelector(
                selectedSize = selectedSize,
                onSizeSelected = { selectedSize = it }
            )
            
            Divider(modifier = Modifier.padding(vertical = 8.dp))
            
            // Location Selection
            Text(
                text = "Pickup & Dropoff Locations",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold
            )
            
            LocationSelectionCard(
                label = "Pickup Location",
                location = pickupLocation,
                onClick = { onNavigateToLocationPicker(true) }
            )
            
            LocationSelectionCard(
                label = "Dropoff Location",
                location = dropoffLocation,
                onClick = { onNavigateToLocationPicker(false) }
            )
            
            Divider(modifier = Modifier.padding(vertical = 8.dp))
            
            // Sender Information
            Text(
                text = "Sender Information",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold
            )
            
            OutlinedTextField(
                value = senderName,
                onValueChange = { senderName = it },
                label = { Text("Sender Name") },
                leadingIcon = { Icon(Icons.Default.Person, contentDescription = null) },
                modifier = Modifier.fillMaxWidth(),
                singleLine = true
            )
            
            OutlinedTextField(
                value = senderPhone,
                onValueChange = { senderPhone = it },
                label = { Text("Sender Phone") },
                leadingIcon = { Icon(Icons.Default.Phone, contentDescription = null) },
                modifier = Modifier.fillMaxWidth(),
                singleLine = true,
                placeholder = { Text("10-digit phone number") }
            )
            
            Divider(modifier = Modifier.padding(vertical = 8.dp))
            
            // Recipient Information
            Text(
                text = "Recipient Information",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold
            )
            
            OutlinedTextField(
                value = recipientName,
                onValueChange = { recipientName = it },
                label = { Text("Recipient Name") },
                leadingIcon = { Icon(Icons.Default.Person, contentDescription = null) },
                modifier = Modifier.fillMaxWidth(),
                singleLine = true
            )
            
            OutlinedTextField(
                value = recipientPhone,
                onValueChange = { recipientPhone = it },
                label = { Text("Recipient Phone") },
                leadingIcon = { Icon(Icons.Default.Phone, contentDescription = null) },
                modifier = Modifier.fillMaxWidth(),
                singleLine = true,
                placeholder = { Text("10-digit phone number") }
            )
            
            Divider(modifier = Modifier.padding(vertical = 8.dp))
            
            // Delivery Instructions (Optional)
            Text(
                text = "Delivery Instructions (Optional)",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold
            )
            
            OutlinedTextField(
                value = instructions,
                onValueChange = { instructions = it },
                label = { Text("Special Instructions") },
                leadingIcon = { Icon(Icons.Default.Info, contentDescription = null) },
                modifier = Modifier.fillMaxWidth(),
                minLines = 3,
                maxLines = 5,
                placeholder = { Text("e.g., Ring doorbell, Leave at gate") }
            )
            
            // Error Message
            if (error != null) {
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
                            text = error ?: "",
                            color = MaterialTheme.colorScheme.onErrorContainer
                        )
                    }
                }
            }
            
            // Request Button
            Button(
                onClick = {
                    if (pickupLocation != null && dropoffLocation != null && selectedSize != null) {
                        viewModel.requestParcelDelivery(
                            pickupLocation = pickupLocation!!,
                            dropoffLocation = dropoffLocation!!,
                            parcelSize = selectedSize!!,
                            senderName = senderName,
                            senderPhone = senderPhone,
                            recipientName = recipientName,
                            recipientPhone = recipientPhone,
                            instructions = instructions.ifBlank { null }
                        )
                    }
                },
                modifier = Modifier
                    .fillMaxWidth()
                    .height(56.dp),
                enabled = !isLoading &&
                        pickupLocation != null &&
                        dropoffLocation != null &&
                        selectedSize != null &&
                        senderName.isNotBlank() &&
                        senderPhone.isNotBlank() &&
                        recipientName.isNotBlank() &&
                        recipientPhone.isNotBlank()
            ) {
                if (isLoading) {
                    CircularProgressIndicator(
                        modifier = Modifier.size(24.dp),
                        color = MaterialTheme.colorScheme.onPrimary
                    )
                } else {
                    Icon(Icons.Default.Send, contentDescription = null)
                    Spacer(modifier = Modifier.width(8.dp))
                    Text("Request Parcel Delivery")
                }
            }
            
            // Success Message
            if (requestSuccess) {
                LaunchedEffect(Unit) {
                    // Navigate to tracking screen or show success dialog
                    onNavigateBack()
                }
            }
        }
    }
}

@Composable
private fun ParcelSizeSelector(
    selectedSize: ParcelSize?,
    onSizeSelected: (ParcelSize) -> Unit,
    modifier: Modifier = Modifier
) {
    Column(
        modifier = modifier
            .fillMaxWidth()
            .selectableGroup(),
        verticalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        ParcelSize.values().forEach { size ->
            ParcelSizeOption(
                size = size,
                selected = selectedSize == size,
                onClick = { onSizeSelected(size) }
            )
        }
    }
}

@Composable
private fun ParcelSizeOption(
    size: ParcelSize,
    selected: Boolean,
    onClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    val (label, description, icon) = when (size) {
        ParcelSize.SMALL -> Triple("Small", "Up to 5kg", Icons.Default.ShoppingBag)
        ParcelSize.MEDIUM -> Triple("Medium", "5-15kg", Icons.Default.ShoppingCart)
        ParcelSize.LARGE -> Triple("Large", "15-30kg", Icons.Default.LocalShipping)
    }
    
    Card(
        modifier = modifier
            .fillMaxWidth()
            .selectable(
                selected = selected,
                onClick = onClick,
                role = Role.RadioButton
            ),
        colors = CardDefaults.cardColors(
            containerColor = if (selected) {
                MaterialTheme.colorScheme.primaryContainer
            } else {
                MaterialTheme.colorScheme.surface
            }
        ),
        border = if (selected) {
            CardDefaults.outlinedCardBorder().copy(
                width = 2.dp,
                brush = androidx.compose.ui.graphics.SolidColor(
                    MaterialTheme.colorScheme.primary
                )
            )
        } else {
            CardDefaults.outlinedCardBorder()
        }
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            horizontalArrangement = Arrangement.spacedBy(16.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Icon(
                imageVector = icon,
                contentDescription = null,
                modifier = Modifier.size(32.dp),
                tint = if (selected) {
                    MaterialTheme.colorScheme.primary
                } else {
                    MaterialTheme.colorScheme.onSurface
                }
            )
            
            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = label,
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold,
                    color = if (selected) {
                        MaterialTheme.colorScheme.onPrimaryContainer
                    } else {
                        MaterialTheme.colorScheme.onSurface
                    }
                )
                Text(
                    text = description,
                    style = MaterialTheme.typography.bodyMedium,
                    color = if (selected) {
                        MaterialTheme.colorScheme.onPrimaryContainer
                    } else {
                        MaterialTheme.colorScheme.onSurfaceVariant
                    }
                )
            }
            
            RadioButton(
                selected = selected,
                onClick = null
            )
        }
    }
}

@Composable
private fun LocationSelectionCard(
    label: String,
    location: Location?,
    onClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    OutlinedCard(
        onClick = onClick,
        modifier = modifier.fillMaxWidth()
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            horizontalArrangement = Arrangement.spacedBy(12.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Icon(
                imageVector = Icons.Default.LocationOn,
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
                    text = location?.address ?: "Tap to select location",
                    style = MaterialTheme.typography.bodyLarge,
                    color = if (location != null) {
                        MaterialTheme.colorScheme.onSurface
                    } else {
                        MaterialTheme.colorScheme.onSurfaceVariant
                    }
                )
            }
            
            Icon(
                imageVector = Icons.Default.KeyboardArrowRight,
                contentDescription = null,
                tint = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }
    }
}
