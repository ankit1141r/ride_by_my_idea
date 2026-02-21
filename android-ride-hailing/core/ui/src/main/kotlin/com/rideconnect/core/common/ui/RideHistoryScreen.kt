package com.rideconnect.core.common.ui

import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import com.rideconnect.core.domain.model.Ride
import com.rideconnect.core.domain.model.RideStatus
import java.text.SimpleDateFormat
import java.util.*

/**
 * Screen displaying ride history with filtering and search
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun RideHistoryScreen(
    rides: List<Ride>,
    isLoading: Boolean,
    onRideClick: (Ride) -> Unit,
    onSearchQueryChange: (String) -> Unit,
    onDateRangeSelected: (Long?, Long?) -> Unit,
    modifier: Modifier = Modifier
) {
    var searchQuery by remember { mutableStateOf("") }
    var showDatePicker by remember { mutableStateOf(false) }
    var showFilterMenu by remember { mutableStateOf(false) }
    
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Ride History") },
                actions = {
                    IconButton(onClick = { showFilterMenu = true }) {
                        Icon(Icons.Default.FilterList, "Filter")
                    }
                }
            )
        },
        modifier = modifier
    ) { paddingValues ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
        ) {
            // Search bar
            OutlinedTextField(
                value = searchQuery,
                onValueChange = {
                    searchQuery = it
                    onSearchQueryChange(it)
                },
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(16.dp),
                placeholder = { Text("Search by location or driver") },
                leadingIcon = {
                    Icon(Icons.Default.Search, "Search")
                },
                trailingIcon = {
                    if (searchQuery.isNotEmpty()) {
                        IconButton(onClick = {
                            searchQuery = ""
                            onSearchQueryChange("")
                        }) {
                            Icon(Icons.Default.Clear, "Clear")
                        }
                    }
                },
                singleLine = true
            )
            
            // Ride list
            if (isLoading) {
                Box(
                    modifier = Modifier.fillMaxSize(),
                    contentAlignment = Alignment.Center
                ) {
                    CircularProgressIndicator()
                }
            } else if (rides.isEmpty()) {
                Box(
                    modifier = Modifier.fillMaxSize(),
                    contentAlignment = Alignment.Center
                ) {
                    Column(
                        horizontalAlignment = Alignment.CenterHorizontally,
                        modifier = Modifier.padding(32.dp)
                    ) {
                        Icon(
                            imageVector = Icons.Default.History,
                            contentDescription = null,
                            modifier = Modifier.size(64.dp),
                            tint = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                        Spacer(modifier = Modifier.height(16.dp))
                        Text(
                            text = "No rides found",
                            style = MaterialTheme.typography.titleMedium,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }
                }
            } else {
                LazyColumn(
                    modifier = Modifier.fillMaxSize(),
                    contentPadding = PaddingValues(16.dp),
                    verticalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    items(rides) { ride ->
                        RideHistoryItem(
                            ride = ride,
                            onClick = { onRideClick(ride) }
                        )
                    }
                }
            }
        }
        
        // Filter menu
        if (showFilterMenu) {
            DateRangeFilterDialog(
                onDismiss = { showFilterMenu = false },
                onDateRangeSelected = { start, end ->
                    onDateRangeSelected(start, end)
                    showFilterMenu = false
                }
            )
        }
    }
}

/**
 * Individual ride history item
 */
@Composable
fun RideHistoryItem(
    ride: Ride,
    onClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier
            .fillMaxWidth()
            .clickable(onClick = onClick),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp)
        ) {
            // Date and status
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                val dateFormatter = SimpleDateFormat("MMM dd, yyyy • hh:mm a", Locale.getDefault())
                Text(
                    text = ride.completedAt?.let { dateFormatter.format(Date(it)) }
                        ?: dateFormatter.format(Date(ride.requestedAt)),
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
                
                RideStatusChip(status = ride.status)
            }
            
            Spacer(modifier = Modifier.height(12.dp))
            
            // Pickup location
            Row(
                verticalAlignment = Alignment.Top,
                modifier = Modifier.fillMaxWidth()
            ) {
                Icon(
                    imageVector = Icons.Default.LocationOn,
                    contentDescription = null,
                    tint = MaterialTheme.colorScheme.primary,
                    modifier = Modifier.size(20.dp)
                )
                Spacer(modifier = Modifier.width(8.dp))
                Text(
                    text = ride.pickupLocation.address ?: "Pickup location",
                    style = MaterialTheme.typography.bodyMedium,
                    maxLines = 1,
                    overflow = TextOverflow.Ellipsis,
                    modifier = Modifier.weight(1f)
                )
            }
            
            Spacer(modifier = Modifier.height(8.dp))
            
            // Dropoff location
            Row(
                verticalAlignment = Alignment.Top,
                modifier = Modifier.fillMaxWidth()
            ) {
                Icon(
                    imageVector = Icons.Default.Place,
                    contentDescription = null,
                    tint = MaterialTheme.colorScheme.error,
                    modifier = Modifier.size(20.dp)
                )
                Spacer(modifier = Modifier.width(8.dp))
                Text(
                    text = ride.dropoffLocation.address ?: "Dropoff location",
                    style = MaterialTheme.typography.bodyMedium,
                    maxLines = 1,
                    overflow = TextOverflow.Ellipsis,
                    modifier = Modifier.weight(1f)
                )
            }
            
            Spacer(modifier = Modifier.height(12.dp))
            
            // Fare and distance
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                ride.fare?.let { fare ->
                    Text(
                        text = "₹%.2f".format(fare),
                        style = MaterialTheme.typography.titleMedium,
                        color = MaterialTheme.colorScheme.primary
                    )
                }
                
                ride.distance?.let { distance ->
                    Text(
                        text = "%.1f km".format(distance),
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
            }
        }
    }
}

/**
 * Chip displaying ride status
 */
@Composable
fun RideStatusChip(
    status: RideStatus,
    modifier: Modifier = Modifier
) {
    val (text, color) = when (status) {
        RideStatus.COMPLETED -> "Completed" to MaterialTheme.colorScheme.primary
        RideStatus.CANCELLED -> "Cancelled" to MaterialTheme.colorScheme.error
        else -> status.name to MaterialTheme.colorScheme.onSurfaceVariant
    }
    
    Surface(
        modifier = modifier,
        shape = MaterialTheme.shapes.small,
        color = color.copy(alpha = 0.1f)
    ) {
        Text(
            text = text,
            style = MaterialTheme.typography.labelSmall,
            color = color,
            modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp)
        )
    }
}

/**
 * Dialog for selecting date range filter
 */
@Composable
fun DateRangeFilterDialog(
    onDismiss: () -> Unit,
    onDateRangeSelected: (Long?, Long?) -> Unit
) {
    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text("Filter by Date") },
        text = {
            Column {
                TextButton(
                    onClick = {
                        onDateRangeSelected(null, null)
                    },
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Text("All Time")
                }
                
                TextButton(
                    onClick = {
                        val now = System.currentTimeMillis()
                        val sevenDaysAgo = now - (7 * 24 * 60 * 60 * 1000L)
                        onDateRangeSelected(sevenDaysAgo, now)
                    },
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Text("Last 7 Days")
                }
                
                TextButton(
                    onClick = {
                        val now = System.currentTimeMillis()
                        val thirtyDaysAgo = now - (30 * 24 * 60 * 60 * 1000L)
                        onDateRangeSelected(thirtyDaysAgo, now)
                    },
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Text("Last 30 Days")
                }
                
                TextButton(
                    onClick = {
                        val now = System.currentTimeMillis()
                        val threeMonthsAgo = now - (90 * 24 * 60 * 60 * 1000L)
                        onDateRangeSelected(threeMonthsAgo, now)
                    },
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Text("Last 3 Months")
                }
            }
        },
        confirmButton = {
            TextButton(onClick = onDismiss) {
                Text("Close")
            }
        }
    )
}
