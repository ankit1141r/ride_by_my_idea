package com.rideconnect.core.domain.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.rideconnect.core.common.result.Result
import com.rideconnect.core.domain.model.*
import com.rideconnect.core.domain.repository.RideRepository
import com.rideconnect.core.domain.websocket.WebSocketManager
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class RideViewModel @Inject constructor(
    private val rideRepository: RideRepository,
    private val webSocketManager: WebSocketManager
) : ViewModel() {
    
    private val _rideState = MutableStateFlow<RideState>(RideState.Idle)
    val rideState: StateFlow<RideState> = _rideState.asStateFlow()
    
    private val _activeRide = MutableStateFlow<Ride?>(null)
    val activeRide: StateFlow<Ride?> = _activeRide.asStateFlow()
    
    private val _fareEstimate = MutableStateFlow<FareEstimate?>(null)
    val fareEstimate: StateFlow<FareEstimate?> = _fareEstimate.asStateFlow()
    
    private val _rideHistory = MutableStateFlow<List<Ride>>(emptyList())
    val rideHistory: StateFlow<List<Ride>> = _rideHistory.asStateFlow()
    
    private val _driverLocation = MutableStateFlow<Location?>(null)
    val driverLocation: StateFlow<Location?> = _driverLocation.asStateFlow()
    
    init {
        observeActiveRide()
        observeDriverLocation()
    }
    
    private fun observeActiveRide() {
        viewModelScope.launch {
            rideRepository.observeActiveRide().collect { ride ->
                _activeRide.value = ride
                
                // Update state based on ride status
                ride?.let {
                    when (it.status) {
                        RideStatus.REQUESTED, RideStatus.SEARCHING -> {
                            _rideState.value = RideState.Searching
                        }
                        RideStatus.ACCEPTED, RideStatus.DRIVER_ARRIVING -> {
                            _rideState.value = RideState.DriverAssigned
                        }
                        RideStatus.ARRIVED -> {
                            _rideState.value = RideState.DriverArrived
                        }
                        RideStatus.IN_PROGRESS -> {
                            _rideState.value = RideState.InProgress
                        }
                        RideStatus.COMPLETED -> {
                            _rideState.value = RideState.Completed
                            _activeRide.value = null
                        }
                        RideStatus.CANCELLED -> {
                            _rideState.value = RideState.Cancelled(it.cancellationReason ?: "Ride cancelled")
                            _activeRide.value = null
                        }
                    }
                }
            }
        }
    }
    
    private fun observeDriverLocation() {
        viewModelScope.launch {
            webSocketManager.messages.collect { message ->
                if (message is com.rideconnect.core.domain.websocket.WebSocketMessage.DriverLocationUpdate) {
                    val currentRide = _activeRide.value
                    if (currentRide?.id == message.rideId) {
                        _driverLocation.value = message.location
                    }
                }
            }
        }
    }
    
    fun requestRide(pickupLocation: Location, dropoffLocation: Location) {
        viewModelScope.launch {
            _rideState.value = RideState.Loading
            
            val request = RideRequest(
                pickupLocation = pickupLocation,
                dropoffLocation = dropoffLocation
            )
            
            when (val result = rideRepository.requestRide(request)) {
                is Result.Success -> {
                    _activeRide.value = result.data
                    _rideState.value = RideState.Searching
                }
                is Result.Error -> {
                    _rideState.value = RideState.Error(
                        result.exception.message ?: "Failed to request ride"
                    )
                }
            }
        }
    }
    
    fun calculateFare(pickupLocation: Location, dropoffLocation: Location) {
        viewModelScope.launch {
            val request = RideRequest(
                pickupLocation = pickupLocation,
                dropoffLocation = dropoffLocation
            )
            
            when (val result = rideRepository.getFareEstimate(request)) {
                is Result.Success -> {
                    _fareEstimate.value = result.data
                }
                is Result.Error -> {
                    _rideState.value = RideState.Error(
                        result.exception.message ?: "Failed to calculate fare"
                    )
                }
            }
        }
    }
    
    fun cancelRide(reason: String) {
        viewModelScope.launch {
            val currentRide = _activeRide.value
            if (currentRide != null) {
                _rideState.value = RideState.Loading
                
                when (val result = rideRepository.cancelRide(currentRide.id, reason)) {
                    is Result.Success -> {
                        _activeRide.value = null
                        _rideState.value = RideState.Cancelled(reason)
                    }
                    is Result.Error -> {
                        _rideState.value = RideState.Error(
                            result.exception.message ?: "Failed to cancel ride"
                        )
                    }
                }
            }
        }
    }
    
    fun loadRideHistory(page: Int = 0, pageSize: Int = 20) {
        viewModelScope.launch {
            when (val result = rideRepository.getRideHistory(page, pageSize)) {
                is Result.Success -> {
                    _rideHistory.value = result.data
                }
                is Result.Error -> {
                    _rideState.value = RideState.Error(
                        result.exception.message ?: "Failed to load ride history"
                    )
                }
            }
        }
    }
    
    fun getRideDetails(rideId: String) {
        viewModelScope.launch {
            _rideState.value = RideState.Loading
            
            when (val result = rideRepository.getRideDetails(rideId)) {
                is Result.Success -> {
                    _activeRide.value = result.data
                    _rideState.value = RideState.Success
                }
                is Result.Error -> {
                    _rideState.value = RideState.Error(
                        result.exception.message ?: "Failed to get ride details"
                    )
                }
            }
        }
    }
    
    fun resetState() {
        _rideState.value = RideState.Idle
    }
    
    fun clearFareEstimate() {
        _fareEstimate.value = null
    }
}

sealed class RideState {
    object Idle : RideState()
    object Loading : RideState()
    object Success : RideState()
    object Searching : RideState()
    object DriverAssigned : RideState()
    object DriverArrived : RideState()
    object InProgress : RideState()
    object Completed : RideState()
    data class Cancelled(val reason: String) : RideState()
    data class Error(val message: String) : RideState()
}
