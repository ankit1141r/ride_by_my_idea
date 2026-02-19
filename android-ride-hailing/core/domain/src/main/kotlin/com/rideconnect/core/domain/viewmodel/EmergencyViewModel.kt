package com.rideconnect.core.domain.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.rideconnect.core.common.result.Result
import com.rideconnect.core.domain.location.LocationService
import com.rideconnect.core.domain.model.EmergencyContact
import com.rideconnect.core.domain.repository.EmergencyRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.launch
import timber.log.Timber
import javax.inject.Inject

/**
 * ViewModel for managing emergency features.
 * Handles SOS activation, emergency contacts, and ride sharing.
 * 
 * Requirements: 9.1, 9.2, 9.3, 9.4, 9.7
 */
@HiltViewModel
class EmergencyViewModel @Inject constructor(
    private val emergencyRepository: EmergencyRepository,
    private val locationService: LocationService
) : ViewModel() {
    
    /**
     * Emergency contacts list.
     * Requirements: 9.7
     */
    val emergencyContacts: StateFlow<List<EmergencyContact>> = emergencyRepository
        .getEmergencyContacts()
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5000),
            initialValue = emptyList()
        )
    
    private val _sosActive = MutableStateFlow(false)
    val sosActive: StateFlow<Boolean> = _sosActive.asStateFlow()
    
    private val _sosState = MutableStateFlow<SOSState>(SOSState.Idle)
    val sosState: StateFlow<SOSState> = _sosState.asStateFlow()
    
    private val _addContactState = MutableStateFlow<AddContactState>(AddContactState.Idle)
    val addContactState: StateFlow<AddContactState> = _addContactState.asStateFlow()
    
    private val _shareRideState = MutableStateFlow<ShareRideState>(ShareRideState.Idle)
    val shareRideState: StateFlow<ShareRideState> = _shareRideState.asStateFlow()
    
    private val _error = MutableStateFlow<String?>(null)
    val error: StateFlow<String?> = _error.asStateFlow()
    
    /**
     * Trigger SOS alert.
     * Requirements: 9.1, 9.2, 9.3, 9.6
     */
    fun triggerSOS(rideId: String) {
        viewModelScope.launch {
            _sosState.value = SOSState.Triggering
            
            // Get current location
            val location = locationService.getCurrentLocation()
            if (location == null) {
                _sosState.value = SOSState.Error("Unable to get current location")
                _error.value = "Unable to get current location"
                return@launch
            }
            
            when (val result = emergencyRepository.triggerSOS(rideId, location)) {
                is Result.Success -> {
                    _sosActive.value = true
                    _sosState.value = SOSState.Active
                    _error.value = null
                    
                    // Increase location update frequency to 5 seconds for SOS
                    // Requirements: 9.6
                    try {
                        locationService.stopLocationUpdates()
                        locationService.startLocationUpdates(5000L) // 5 seconds
                        Timber.d("Location update frequency increased to 5 seconds for SOS")
                    } catch (e: Exception) {
                        Timber.e(e, "Failed to increase location update frequency")
                    }
                    
                    Timber.d("SOS triggered successfully for ride: $rideId")
                }
                is Result.Error -> {
                    _sosState.value = SOSState.Error(result.message)
                    _error.value = result.message
                    Timber.e("Failed to trigger SOS: ${result.message}")
                }
            }
        }
    }
    
    /**
     * Add an emergency contact.
     * Requirements: 9.7
     */
    fun addEmergencyContact(contact: EmergencyContact) {
        viewModelScope.launch {
            _addContactState.value = AddContactState.Adding
            
            when (val result = emergencyRepository.addEmergencyContact(contact)) {
                is Result.Success -> {
                    _addContactState.value = AddContactState.Success
                    _error.value = null
                    Timber.d("Emergency contact added: ${contact.name}")
                    // Reset to idle after a short delay
                    kotlinx.coroutines.delay(500)
                    _addContactState.value = AddContactState.Idle
                }
                is Result.Error -> {
                    _addContactState.value = AddContactState.Error(result.message)
                    _error.value = result.message
                    Timber.e("Failed to add emergency contact: ${result.message}")
                }
            }
        }
    }
    
    /**
     * Remove an emergency contact.
     * Requirements: 9.7
     */
    fun removeEmergencyContact(contactId: String) {
        viewModelScope.launch {
            when (val result = emergencyRepository.removeEmergencyContact(contactId)) {
                is Result.Success -> {
                    _error.value = null
                    Timber.d("Emergency contact removed: $contactId")
                }
                is Result.Error -> {
                    _error.value = result.message
                    Timber.e("Failed to remove emergency contact: ${result.message}")
                }
            }
        }
    }
    
    /**
     * Share ride with emergency contacts.
     * Requirements: 9.4
     */
    fun shareRide(rideId: String, contactIds: List<String>) {
        viewModelScope.launch {
            _shareRideState.value = ShareRideState.Sharing
            
            when (val result = emergencyRepository.shareRideWithContacts(rideId, contactIds)) {
                is Result.Success -> {
                    _shareRideState.value = ShareRideState.Success(result.data.shareUrl)
                    _error.value = null
                    Timber.d("Ride shared successfully: ${result.data.shareUrl}")
                }
                is Result.Error -> {
                    _shareRideState.value = ShareRideState.Error(result.message)
                    _error.value = result.message
                    Timber.e("Failed to share ride: ${result.message}")
                }
            }
        }
    }
    
    /**
     * Deactivate SOS.
     * Restores normal location update frequency.
     */
    fun deactivateSOS() {
        _sosActive.value = false
        _sosState.value = SOSState.Idle
        
        // Restore normal location update frequency (10 seconds)
        viewModelScope.launch {
            try {
                locationService.stopLocationUpdates()
                locationService.startLocationUpdates(10000L) // 10 seconds
                Timber.d("Location update frequency restored to 10 seconds")
            } catch (e: Exception) {
                Timber.e(e, "Failed to restore location update frequency")
            }
        }
    }
    
    /**
     * Clear error message.
     */
    fun clearError() {
        _error.value = null
    }
    
    /**
     * Reset add contact state.
     */
    fun resetAddContactState() {
        _addContactState.value = AddContactState.Idle
    }
    
    /**
     * Reset share ride state.
     */
    fun resetShareRideState() {
        _shareRideState.value = ShareRideState.Idle
    }
}

/**
 * State for SOS operation.
 */
sealed class SOSState {
    object Idle : SOSState()
    object Triggering : SOSState()
    object Active : SOSState()
    data class Error(val message: String) : SOSState()
}

/**
 * State for adding emergency contact.
 */
sealed class AddContactState {
    object Idle : AddContactState()
    object Adding : AddContactState()
    object Success : AddContactState()
    data class Error(val message: String) : AddContactState()
}

/**
 * State for sharing ride.
 */
sealed class ShareRideState {
    object Idle : ShareRideState()
    object Sharing : ShareRideState()
    data class Success(val shareUrl: String) : ShareRideState()
    data class Error(val message: String) : ShareRideState()
}
