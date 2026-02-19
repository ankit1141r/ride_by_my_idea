package com.rideconnect.core.domain.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.rideconnect.core.common.result.Result
import com.rideconnect.core.domain.model.Location
import com.rideconnect.core.domain.model.ScheduledRide
import com.rideconnect.core.domain.model.ScheduledRideRequest
import com.rideconnect.core.domain.repository.ScheduledRideRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import java.util.concurrent.TimeUnit
import javax.inject.Inject

/**
 * ViewModel for scheduled ride management.
 * 
 * Requirements: 4.1, 4.2, 4.3, 4.7
 */
@HiltViewModel
class ScheduledRideViewModel @Inject constructor(
    private val scheduledRideRepository: ScheduledRideRepository
) : ViewModel() {

    private val _scheduledRides = MutableStateFlow<List<ScheduledRide>>(emptyList())
    val scheduledRides: StateFlow<List<ScheduledRide>> = _scheduledRides.asStateFlow()

    private val _isLoading = MutableStateFlow(false)
    val isLoading: StateFlow<Boolean> = _isLoading.asStateFlow()

    private val _error = MutableStateFlow<String?>(null)
    val error: StateFlow<String?> = _error.asStateFlow()

    private val _scheduleSuccess = MutableStateFlow(false)
    val scheduleSuccess: StateFlow<Boolean> = _scheduleSuccess.asStateFlow()

    companion object {
        // Requirement 4.3: Minimum 1 hour advance scheduling
        private val MIN_ADVANCE_TIME_MS = TimeUnit.HOURS.toMillis(1)
        
        // Requirement 4.2: Maximum 7 days advance scheduling
        private val MAX_ADVANCE_TIME_MS = TimeUnit.DAYS.toMillis(7)
    }

    init {
        loadScheduledRides()
        observeScheduledRides()
    }

    /**
     * Schedule a new ride with validation.
     * Requirements: 4.1, 4.2, 4.3
     */
    fun scheduleRide(
        pickupLocation: Location,
        dropoffLocation: Location,
        scheduledTime: Long
    ) {
        viewModelScope.launch {
            _isLoading.value = true
            _error.value = null
            _scheduleSuccess.value = false

            // Validate scheduling time
            val validationError = validateScheduledTime(scheduledTime)
            if (validationError != null) {
                _error.value = validationError
                _isLoading.value = false
                return@launch
            }

            val request = ScheduledRideRequest(
                pickupLocation = pickupLocation,
                dropoffLocation = dropoffLocation,
                scheduledTime = scheduledTime
            )

            when (val result = scheduledRideRepository.scheduleRide(request)) {
                is Result.Success -> {
                    _scheduleSuccess.value = true
                    loadScheduledRides()
                }
                is Result.Error -> {
                    _error.value = result.message
                }
            }

            _isLoading.value = false
        }
    }

    /**
     * Cancel a scheduled ride.
     * Requirements: 4.6
     */
    fun cancelScheduledRide(rideId: String, reason: String) {
        viewModelScope.launch {
            _isLoading.value = true
            _error.value = null

            when (val result = scheduledRideRepository.cancelScheduledRide(rideId, reason)) {
                is Result.Success -> {
                    loadScheduledRides()
                }
                is Result.Error -> {
                    _error.value = result.message
                }
            }

            _isLoading.value = false
        }
    }

    /**
     * Load scheduled rides from repository.
     * Requirements: 4.7
     */
    fun loadScheduledRides() {
        viewModelScope.launch {
            _isLoading.value = true
            _error.value = null

            when (val result = scheduledRideRepository.getScheduledRides()) {
                is Result.Success -> {
                    _scheduledRides.value = result.data
                }
                is Result.Error -> {
                    _error.value = result.message
                }
            }

            _isLoading.value = false
        }
    }

    /**
     * Observe scheduled rides from local database.
     * Requirements: 4.7
     */
    private fun observeScheduledRides() {
        viewModelScope.launch {
            scheduledRideRepository.observeScheduledRides().collect { rides ->
                _scheduledRides.value = rides
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
     * Reset schedule success flag.
     */
    fun resetScheduleSuccess() {
        _scheduleSuccess.value = false
    }

    /**
     * Validate scheduled time against requirements.
     * Requirements: 4.2, 4.3
     * 
     * @return Error message if validation fails, null if valid
     */
    private fun validateScheduledTime(scheduledTime: Long): String? {
        val currentTime = System.currentTimeMillis()
        val timeDifference = scheduledTime - currentTime

        // Requirement 4.3: Minimum 1 hour in advance
        if (timeDifference < MIN_ADVANCE_TIME_MS) {
            return "Scheduled time must be at least 1 hour in the future"
        }

        // Requirement 4.2: Maximum 7 days in advance
        if (timeDifference > MAX_ADVANCE_TIME_MS) {
            return "Scheduled time cannot be more than 7 days in the future"
        }

        return null
    }
}
