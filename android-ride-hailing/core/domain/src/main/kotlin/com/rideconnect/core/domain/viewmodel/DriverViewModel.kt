package com.rideconnect.core.domain.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.rideconnect.core.domain.model.Ride
import com.rideconnect.core.domain.model.ParcelDelivery
import com.rideconnect.core.domain.repository.DriverRideRepository
import com.rideconnect.core.domain.repository.ParcelRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.launch
import javax.inject.Inject

data class DriverUiState(
    val isOnline: Boolean = false,
    val activeRide: Ride? = null,
    val activeParcel: ParcelDelivery? = null,
    val incomingRideRequest: Ride? = null,
    val incomingParcelRequest: ParcelDelivery? = null,
    val rideRequestQueue: List<Ride> = emptyList(),
    val acceptsParcelDelivery: Boolean = false,
    val isLoading: Boolean = false,
    val error: String? = null
)

@HiltViewModel
class DriverViewModel @Inject constructor(
    private val driverRideRepository: DriverRideRepository,
    private val parcelRepository: ParcelRepository,
    private val earningsRepository: com.rideconnect.core.domain.repository.EarningsRepository
) : ViewModel() {
    
    private val _uiState = MutableStateFlow(DriverUiState())
    val uiState: StateFlow<DriverUiState> = _uiState.asStateFlow()
    
    init {
        observeActiveRide()
        observeActiveParcel()
        observeRideRequests()
        observeParcelRequests()
    }
    
    private fun observeActiveRide() {
        viewModelScope.launch {
            driverRideRepository.observeActiveRide()
                .collect { ride ->
                    _uiState.update { it.copy(activeRide = ride) }
                }
        }
    }
    
    private fun observeActiveParcel() {
        viewModelScope.launch {
            parcelRepository.observeActiveParcel()
                .collect { parcel ->
                    _uiState.update { it.copy(activeParcel = parcel) }
                }
        }
    }
    
    private fun observeRideRequests() {
        viewModelScope.launch {
            driverRideRepository.observeRideRequests()
                .filterNotNull() // Filter out null values
                .collect { request ->
                    _uiState.update { state ->
                        // If there's already an incoming request being displayed, queue the new one
                        if (state.incomingRideRequest != null) {
                            state.copy(
                                rideRequestQueue = state.rideRequestQueue + request
                            )
                        } else {
                            // Display the request immediately if no request is currently shown
                            state.copy(incomingRideRequest = request)
                        }
                    }
                }
        }
    }
    
    private fun showNextQueuedRequest() {
        _uiState.update { state ->
            val queue = state.rideRequestQueue
            if (queue.isNotEmpty()) {
                state.copy(
                    incomingRideRequest = queue.first(),
                    rideRequestQueue = queue.drop(1)
                )
            } else {
                state.copy(incomingRideRequest = null)
            }
        }
    }
    
    private fun observeParcelRequests() {
        viewModelScope.launch {
            parcelRepository.observeActiveParcel()
                .filter { it?.status == com.rideconnect.core.domain.model.ParcelStatus.REQUESTED }
                .collect { parcel ->
                    if (_uiState.value.acceptsParcelDelivery) {
                        _uiState.update { it.copy(incomingParcelRequest = parcel) }
                    }
                }
        }
    }
    
    fun toggleAvailability() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, error = null) }
            
            val newStatus = !_uiState.value.isOnline
            driverRideRepository.setAvailability(newStatus)
                .onSuccess {
                    _uiState.update { it.copy(isOnline = newStatus, isLoading = false) }
                }
                .onError { exception ->
                    _uiState.update { 
                        it.copy(
                            isLoading = false,
                            error = exception.message ?: "Failed to update availability"
                        )
                    }
                }
        }
    }
    
    fun setParcelDeliveryPreference(accepts: Boolean) {
        viewModelScope.launch {
            _uiState.update { it.copy(acceptsParcelDelivery = accepts) }
            // Store preference locally or sync with backend
        }
    }
    
    fun acceptRide(rideId: String) {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, error = null) }
            
            driverRideRepository.acceptRide(rideId)
                .onSuccess { ride ->
                    _uiState.update { 
                        it.copy(
                            activeRide = ride,
                            incomingRideRequest = null,
                            rideRequestQueue = emptyList(), // Clear queue when accepting a ride
                            isLoading = false
                        )
                    }
                }
                .onError { exception ->
                    _uiState.update { 
                        it.copy(
                            isLoading = false,
                            error = exception.message ?: "Failed to accept ride"
                        )
                    }
                    // Show next queued request on failure
                    showNextQueuedRequest()
                }
        }
    }
    
    fun rejectRide(rideId: String, reason: String = "Driver declined") {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, error = null) }
            
            driverRideRepository.rejectRide(rideId, reason)
                .onSuccess {
                    _uiState.update { it.copy(isLoading = false) }
                    // Show next queued request after rejection
                    showNextQueuedRequest()
                }
                .onError { exception ->
                    _uiState.update { 
                        it.copy(
                            isLoading = false,
                            error = exception.message ?: "Failed to reject ride"
                        )
                    }
                    // Show next queued request even on failure
                    showNextQueuedRequest()
                }
        }
    }
    
    fun acceptParcelDelivery(deliveryId: String) {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, error = null) }
            
            // Accept parcel delivery through repository
            parcelRepository.getParcelDetails(deliveryId)
                .onSuccess { parcel ->
                    _uiState.update { 
                        it.copy(
                            activeParcel = parcel,
                            incomingParcelRequest = null,
                            isLoading = false
                        )
                    }
                }
                .onError { exception ->
                    _uiState.update { 
                        it.copy(
                            isLoading = false,
                            error = exception.message ?: "Failed to accept parcel delivery"
                        )
                    }
                }
        }
    }
    
    fun rejectParcelDelivery(deliveryId: String, reason: String) {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, error = null) }
            
            // Reject parcel delivery
            _uiState.update { 
                it.copy(
                    incomingParcelRequest = null,
                    isLoading = false
                )
            }
        }
    }
    
    fun confirmPickup(deliveryId: String) {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, error = null) }
            
            parcelRepository.confirmPickup(deliveryId)
                .onSuccess {
                    _uiState.update { it.copy(isLoading = false) }
                }
                .onError { exception ->
                    _uiState.update { 
                        it.copy(
                            isLoading = false,
                            error = exception.message ?: "Failed to confirm pickup"
                        )
                    }
                }
        }
    }
    
    fun confirmDelivery(deliveryId: String) {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, error = null) }
            
            parcelRepository.confirmDelivery(deliveryId)
                .onSuccess {
                    _uiState.update { 
                        it.copy(
                            activeParcel = null,
                            isLoading = false
                        )
                    }
                }
                .onError { exception ->
                    _uiState.update { 
                        it.copy(
                            isLoading = false,
                            error = exception.message ?: "Failed to confirm delivery"
                        )
                    }
                }
        }
    }
    
    fun startRide() {
        viewModelScope.launch {
            val rideId = _uiState.value.activeRide?.id ?: return@launch
            
            _uiState.update { it.copy(isLoading = true, error = null) }
            
            driverRideRepository.startRide(rideId)
                .onSuccess {
                    _uiState.update { it.copy(isLoading = false) }
                }
                .onError { exception ->
                    _uiState.update { 
                        it.copy(
                            isLoading = false,
                            error = exception.message ?: "Failed to start ride"
                        )
                    }
                }
        }
    }
    
    fun completeRide() {
        viewModelScope.launch {
            val rideId = _uiState.value.activeRide?.id ?: return@launch
            
            _uiState.update { it.copy(isLoading = true, error = null) }
            
            driverRideRepository.completeRide(rideId)
                .onSuccess {
                    _uiState.update { 
                        it.copy(
                            activeRide = null,
                            isLoading = false
                        )
                    }
                    // Refresh earnings after ride completion
                    // Requirements: 14.3
                    refreshEarnings()
                }
                .onError { exception ->
                    _uiState.update { 
                        it.copy(
                            isLoading = false,
                            error = exception.message ?: "Failed to complete ride"
                        )
                    }
                }
        }
    }
    
    /**
     * Refresh earnings data after ride completion.
     * Requirements: 14.3
     */
    private fun refreshEarnings() {
        viewModelScope.launch {
            // Sync earnings with backend to get updated data
            val driverId = "current_driver_id" // TODO: Get from auth state
            earningsRepository.syncEarnings(driverId)
        }
    }
    
    fun cancelRide(reason: String) {
        viewModelScope.launch {
            val rideId = _uiState.value.activeRide?.id ?: return@launch
            
            _uiState.update { it.copy(isLoading = true, error = null) }
            
            driverRideRepository.cancelRide(rideId, reason)
                .onSuccess {
                    _uiState.update { 
                        it.copy(
                            activeRide = null,
                            isLoading = false
                        )
                    }
                }
                .onError { exception ->
                    _uiState.update { 
                        it.copy(
                            isLoading = false,
                            error = exception.message ?: "Failed to cancel ride"
                        )
                    }
                }
        }
    }

    /**
     * Rate a rider after ride completion.
     * Requirements: 16.4
     */
    fun rateRider(rideId: String, rating: Int, review: String? = null) {
        viewModelScope.launch {
            // This would call a rating repository method
            // For now, we'll just log the action
            // In a full implementation, this would submit the rating to the backend
        }
    }
    
    /**
     * Show rider rating dialog after ride completion.
     * Requirements: 16.4
     */
    fun shouldShowRiderRatingDialog(): Boolean {
        return _uiState.value.activeRide?.let { ride ->
            ride.status == com.rideconnect.core.domain.model.RideStatus.COMPLETED
        } ?: false
    }
}