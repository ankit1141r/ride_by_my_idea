package com.rideconnect.core.domain.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.rideconnect.core.common.result.Result
import com.rideconnect.core.domain.location.LocationRepository
import com.rideconnect.core.domain.model.Location
import com.rideconnect.core.domain.model.Place
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.FlowPreview
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.launch
import timber.log.Timber
import javax.inject.Inject

/**
 * ViewModel for location search functionality.
 * Manages search query, results, and place selection.
 * 
 * Requirements: 18.3, 18.4
 */
@OptIn(FlowPreview::class)
@HiltViewModel
class LocationSearchViewModel @Inject constructor(
    private val locationRepository: LocationRepository
) : ViewModel() {
    
    private val _searchQuery = MutableStateFlow("")
    val searchQuery: StateFlow<String> = _searchQuery.asStateFlow()
    
    private val _searchResults = MutableStateFlow<List<Place>>(emptyList())
    val searchResults: StateFlow<List<Place>> = _searchResults.asStateFlow()
    
    private val _selectedPlace = MutableStateFlow<Place?>(null)
    val selectedPlace: StateFlow<Place?> = _selectedPlace.asStateFlow()
    
    private val _isLoading = MutableStateFlow(false)
    val isLoading: StateFlow<Boolean> = _isLoading.asStateFlow()
    
    private val _error = MutableStateFlow<String?>(null)
    val error: StateFlow<String?> = _error.asStateFlow()
    
    private val _currentLocation = MutableStateFlow<Location?>(null)
    val currentLocation: StateFlow<Location?> = _currentLocation.asStateFlow()
    
    init {
        // Debounce search queries to avoid excessive API calls
        viewModelScope.launch {
            _searchQuery
                .debounce(300) // Wait 300ms after user stops typing
                .filter { it.length >= 3 } // Only search if query is at least 3 characters
                .distinctUntilChanged()
                .collect { query ->
                    performSearch(query)
                }
        }
    }
    
    /**
     * Update the search query.
     * Search will be triggered automatically after debounce.
     */
    fun updateSearchQuery(query: String) {
        _searchQuery.value = query
        if (query.isEmpty()) {
            _searchResults.value = emptyList()
        }
    }
    
    /**
     * Manually trigger search (e.g., when user presses search button).
     */
    fun search(query: String) {
        _searchQuery.value = query
        if (query.length >= 3) {
            performSearch(query)
        }
    }
    
    /**
     * Perform the actual search using the repository.
     */
    private fun performSearch(query: String) {
        viewModelScope.launch {
            _isLoading.value = true
            _error.value = null
            
            try {
                when (val result = locationRepository.searchPlaces(query, _currentLocation.value)) {
                    is Result.Success -> {
                        _searchResults.value = result.data
                        Timber.d("Search completed: ${result.data.size} results")
                    }
                    is Result.Error -> {
                        _error.value = result.exception.message ?: "Search failed"
                        _searchResults.value = emptyList()
                        Timber.e(result.exception, "Search error")
                    }
                }
            } catch (e: Exception) {
                _error.value = e.message ?: "Unknown error"
                _searchResults.value = emptyList()
                Timber.e(e, "Unexpected search error")
            } finally {
                _isLoading.value = false
            }
        }
    }
    
    /**
     * Select a place from search results.
     * Fetches full place details including coordinates.
     */
    fun selectPlace(place: Place) {
        viewModelScope.launch {
            _isLoading.value = true
            _error.value = null
            
            try {
                // If place already has coordinates, use it directly
                if (place.location.latitude != 0.0 && place.location.longitude != 0.0) {
                    _selectedPlace.value = place
                    _searchQuery.value = place.name
                    _searchResults.value = emptyList()
                } else {
                    // Fetch full place details to get coordinates
                    when (val result = locationRepository.getPlaceDetails(place.placeId)) {
                        is Result.Success -> {
                            _selectedPlace.value = result.data
                            _searchQuery.value = result.data.name
                            _searchResults.value = emptyList()
                            Timber.d("Place selected: ${result.data.name}")
                        }
                        is Result.Error -> {
                            _error.value = result.exception.message ?: "Failed to get place details"
                            Timber.e(result.exception, "Error fetching place details")
                        }
                    }
                }
            } catch (e: Exception) {
                _error.value = e.message ?: "Unknown error"
                Timber.e(e, "Unexpected error selecting place")
            } finally {
                _isLoading.value = false
            }
        }
    }
    
    /**
     * Update current location for biasing search results.
     */
    fun updateCurrentLocation(location: Location) {
        _currentLocation.value = location
    }
    
    /**
     * Clear the selected place.
     */
    fun clearSelection() {
        _selectedPlace.value = null
        _searchQuery.value = ""
        _searchResults.value = emptyList()
    }
    
    /**
     * Clear error message.
     */
    fun clearError() {
        _error.value = null
    }
}
