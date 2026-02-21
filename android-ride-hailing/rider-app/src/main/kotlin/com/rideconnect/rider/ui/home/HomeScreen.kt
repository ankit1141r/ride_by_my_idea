package com.rideconnect.rider.ui.home

import androidx.compose.foundation.layout.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.rideconnect.core.domain.viewmodel.RideViewModel

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun HomeScreen(
    onNavigateToRideRequest: () -> Unit,
    onNavigateToScheduleRide: () -> Unit,
    onNavigateToParcelDelivery: () -> Unit,
    onNavigateToRideTracking: (String) -> Unit,
    onNavigateToSettings: () -> Unit,
    viewModel: RideViewModel = hiltViewModel()
) {
    val activeRide by viewModel.activeRide.collectAsStateWithLifecycle()
    
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("RideConnect") },
                actions = {
                    IconButton(onClick = onNavigateToSettings) {
                        Icon(
                            imageVector = Icons.Default.Settings,
                            contentDescription = "Settings"
                        )
                    }
                }
            )
        }
    ) { paddingValues ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
                .padding(16.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Text(
                text = "Welcome to RideConnect!",
                style = MaterialTheme.typography.headlineMedium,
                modifier = Modifier.padding(bottom = 24.dp)
            )
            
            // Show active ride if exists
            activeRide?.let { ride ->
                Card(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(bottom = 16.dp),
                    onClick = { onNavigateToRideTracking(ride.id) }
                ) {
                    Column(
                        modifier = Modifier.padding(16.dp)
                    ) {
                        Text(
                            text = "Active Ride",
                            style = MaterialTheme.typography.titleMedium,
                            modifier = Modifier.padding(bottom = 8.dp)
                        )
                        Text(
                            text = "Status: ${ride.status}",
                            style = MaterialTheme.typography.bodyMedium
                        )
                        Button(
                            onClick = { onNavigateToRideTracking(ride.id) },
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(top = 8.dp)
                        ) {
                            Text("Track Ride")
                        }
                    }
                }
            }
            
            // Service options
            Text(
                text = "Choose a service",
                style = MaterialTheme.typography.titleLarge,
                modifier = Modifier.padding(bottom = 16.dp)
            )
            
            // Request Ride button
            ElevatedCard(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(bottom = 12.dp),
                onClick = onNavigateToRideRequest
            ) {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(16.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Icon(
                        imageVector = Icons.Default.DirectionsCar,
                        contentDescription = null,
                        modifier = Modifier
                            .size(48.dp)
                            .padding(end = 16.dp)
                    )
                    Column {
                        Text(
                            text = "Request a Ride",
                            style = MaterialTheme.typography.titleMedium
                        )
                        Text(
                            text = "Get a ride now",
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }
                }
            }
            
            // Schedule Ride button
            ElevatedCard(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(bottom = 12.dp),
                onClick = onNavigateToScheduleRide
            ) {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(16.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Icon(
                        imageVector = Icons.Default.Schedule,
                        contentDescription = null,
                        modifier = Modifier
                            .size(48.dp)
                            .padding(end = 16.dp)
                    )
                    Column {
                        Text(
                            text = "Schedule a Ride",
                            style = MaterialTheme.typography.titleMedium
                        )
                        Text(
                            text = "Book for later",
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }
                }
            }
            
            // Parcel Delivery button
            ElevatedCard(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(bottom = 12.dp),
                onClick = onNavigateToParcelDelivery
            ) {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(16.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Icon(
                        imageVector = Icons.Default.LocalShipping,
                        contentDescription = null,
                        modifier = Modifier
                            .size(48.dp)
                            .padding(end = 16.dp)
                    )
                    Column {
                        Text(
                            text = "Send a Parcel",
                            style = MaterialTheme.typography.titleMedium
                        )
                        Text(
                            text = "Deliver packages",
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }
                }
            }
        }
    }
}
