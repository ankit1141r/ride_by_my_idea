package com.rideconnect.core.domain.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.rideconnect.core.domain.location.LocationService
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

/**
 * ViewModel for managing location permission state.
 * 
 * Requirements: 29.1, 29.2, 29.7
 */
@HiltViewModel
class LocationPermissionViewModel @Inject constructor(
    private val locationService: LocationService
) : ViewModel() {
    
    private val _permissionState = MutableStateFlow<LocationPermissionState>(
        LocationPermissionState.NotRequested
    )
    val permissionState: StateFlow<LocationPermissionState> = _permissionState.asStateFlow()
    
    private val _locationEnabled = MutableStateFlow(false)
    val locationEnabled: StateFlow<Boolean> = _locationEnabled.asStateFlow()
    
    init {
        checkLocationEnabled()
    }
    
    fun onPermissionGranted() {
        _permissionState.value = LocationPermissionState.Granted
        checkLocationEnabled()
    }
    
    fun onPermissionDenied() {
        _permissionState.value = LocationPermissionState.Denied
    }
    
    fun onBackgroundPermissionGranted() {
        _permissionState.value = LocationPermissionState.BackgroundGranted
    }
    
    fun onBackgroundPermissionDenied() {
        _permissionState.value = LocationPermissionState.BackgroundDenied
    }
    
    fun checkLocationEnabled() {
        viewModelScope.launch {
            _locationEnabled.value = locationService.isLocationEnabled()
        }
    }
    
    fun hasLocationPermission(): Boolean {
        return locationService.hasLocationPermission()
    }
}

sealed class LocationPermissionState {
    object NotRequested : LocationPermissionState()
    object Granted : LocationPermissionState()
    object Denied : LocationPermissionState()
    object BackgroundGranted : LocationPermissionState()
    object BackgroundDenied : LocationPermissionState()
}
