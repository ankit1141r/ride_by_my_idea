package com.rideconnect.core.common.ui

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import com.rideconnect.core.domain.viewmodel.LocationSearchViewModel

/**
 * Example screen demonstrating LocationSearchBar usage.
 * This can be used in both Rider and Driver apps for location selection.
 * 
 * Requirements: 18.3, 18.4
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun LocationSearchScreen(
    viewModel: LocationSearchViewModel = hiltViewModel(),
    onLocationSelected: (Double, Double, String) -> Unit = { _, _, _ -> },
    modifier: Modifier = Modifier
) {
    val searchQuery by viewModel.searchQuery.collectAsState()
    val searchResults by viewModel.searchResults.collectAsState()
    val selectedPlace by viewModel.selectedPlace.collectAsState()
    val isLoading by viewModel.isLoading.collectAsState()
    val error by viewModel.error.collectAsState()
    
    // Handle place selection
    LaunchedEffect(selectedPlace) {
        selectedPlace?.let { place ->
            onLocationSelected(place.location.latitude, place.location.longitude, place.address)
        }
    }
    
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Search Location") }
            )
        }
    ) { paddingValues ->
        Column(
            modifier = modifier
                .fillMaxSize()
                .padding(paddingValues)
                .padding(16.dp)
        ) {
            LocationSearchBar(
                query = searchQuery,
                onQueryChange = { viewModel.updateSearchQuery(it) },
                searchResults = searchResults,
                onPlaceSelected = { viewModel.selectPlace(it) },
                onSearch = { viewModel.search(it) },
                isLoading = isLoading,
                placeholder = "Enter pickup location"
            )
            
            Spacer(modifier = Modifier.height(16.dp))
            
            // Display selected location
            selectedPlace?.let { place ->
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    colors = CardDefaults.cardColors(
                        containerColor = MaterialTheme.colorScheme.primaryContainer
                    )
                ) {
                    Column(
                        modifier = Modifier.padding(16.dp)
                    ) {
                        Text(
                            text = "Selected Location",
                            style = MaterialTheme.typography.titleMedium
                        )
                        Spacer(modifier = Modifier.height(8.dp))
                        Text(
                            text = place.name,
                            style = MaterialTheme.typography.bodyLarge
                        )
                        Text(
                            text = place.address,
                            style = MaterialTheme.typography.bodyMedium,
                            color = MaterialTheme.colorScheme.onPrimaryContainer.copy(alpha = 0.7f)
                        )
                        Text(
                            text = "Lat: ${place.location.latitude}, Lng: ${place.location.longitude}",
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onPrimaryContainer.copy(alpha = 0.5f)
                        )
                    }
                }
            }
            
            // Display error if any
            error?.let { errorMessage ->
                Spacer(modifier = Modifier.height(16.dp))
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    colors = CardDefaults.cardColors(
                        containerColor = MaterialTheme.colorScheme.errorContainer
                    )
                ) {
                    Text(
                        text = errorMessage,
                        modifier = Modifier.padding(16.dp),
                        color = MaterialTheme.colorScheme.onErrorContainer
                    )
                }
            }
        }
    }
}
