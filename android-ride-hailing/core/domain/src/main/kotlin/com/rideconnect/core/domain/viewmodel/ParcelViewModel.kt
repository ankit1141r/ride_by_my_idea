package com.rideconnect.core.domain.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.rideconnect.core.common.result.Result
import com.rideconnect.core.domain.model.Location
import com.rideconnect.core.domain.model.ParcelDelivery
import com.rideconnect.core.domain.model.ParcelDeliveryRequest
import com.rideconnect.core.domain.model.ParcelSize
import com.rideconnect.core.domain.repository.ParcelRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

/**
 * ViewModel for parcel delivery management in Rider App.
 * 
 * Manages parcel delivery request state, sender/recipient information,
 * and tracks parcel status.
 * 
 * Requirements: 5.1, 5.2, 5.3, 5.4, 5.5
 */
@HiltViewModel
class ParcelViewModel @Inject constructor(
    private val parcelRepository: ParcelRepository
) : ViewModel() {

    // Active parcel delivery
    private val _activeParcel = MutableStateFlow<ParcelDelivery?>(null)
    val activeParcel: StateFlow<ParcelDelivery?> = _activeParcel.asStateFlow()

    // Parcel delivery history
    private val _parcelHistory = MutableStateFlow<List<ParcelDelivery>>(emptyList())
    val parcelHistory: StateFlow<List<ParcelDelivery>> = _parcelHistory.asStateFlow()

    // Loading state
    private val _isLoading = MutableStateFlow(false)
    val isLoading: StateFlow<Boolean> = _isLoading.asStateFlow()

    // Error state
    private val _error = MutableStateFlow<String?>(null)
    val error: StateFlow<String?> = _error.asStateFlow()

    // Request success state
    private val _requestSuccess = MutableStateFlow(false)
    val requestSuccess: StateFlow<Boolean> = _requestSuccess.asStateFlow()

    init {
        observeActiveParcel()
    }

    /**
     * Observe active parcel delivery for real-time updates.
     * Requirements: 5.6, 5.7
     */
    private fun observeActiveParcel() {
        viewModelScope.launch {
            parcelRepository.observeActiveParcel().collect { parcel ->
                _activeParcel.value = parcel
            }
        }
    }

    /**
     * Request a parcel delivery.
     * 
     * Validates all required fields and sends request to backend.
     * Requirements: 5.1, 5.2, 5.3
     * 
     * @param pickupLocation Pickup location
     * @param dropoffLocation Dropoff location
     * @param parcelSize Size of the parcel (SMALL, MEDIUM, LARGE)
     * @param senderName Name of the sender
     * @param senderPhone Phone number of the sender
     * @param recipientName Name of the recipient
     * @param recipientPhone Phone number of the recipient
     * @param instructions Optional delivery instructions
     */
    fun requestParcelDelivery(
        pickupLocation: Location,
        dropoffLocation: Location,
        parcelSize: ParcelSize,
        senderName: String,
        senderPhone: String,
        recipientName: String,
        recipientPhone: String,
        instructions: String?
    ) {
        viewModelScope.launch {
            _isLoading.value = true
            _error.value = null
            _requestSuccess.value = false

            // Validate inputs
            val validationError = validateParcelRequest(
                senderName, senderPhone, recipientName, recipientPhone
            )
            if (validationError != null) {
                _error.value = validationError
                _isLoading.value = false
                return@launch
            }

            val request = ParcelDeliveryRequest(
                pickupLocation = pickupLocation,
                dropoffLocation = dropoffLocation,
                parcelSize = parcelSize,
                senderName = senderName.trim(),
                senderPhone = senderPhone.trim(),
                recipientName = recipientName.trim(),
                recipientPhone = recipientPhone.trim(),
                instructions = instructions?.trim()
            )

            when (val result = parcelRepository.requestParcelDelivery(request)) {
                is Result.Success -> {
                    _activeParcel.value = result.data
                    _requestSuccess.value = true
                }
                is Result.Error -> {
                    _error.value = result.message
                }
            }

            _isLoading.value = false
        }
    }

    /**
     * Validate parcel delivery request fields.
     * Requirements: 5.1, 5.2
     * 
     * @return Error message if validation fails, null otherwise
     */
    private fun validateParcelRequest(
        senderName: String,
        senderPhone: String,
        recipientName: String,
        recipientPhone: String
    ): String? {
        if (senderName.isBlank()) {
            return "Sender name is required"
        }
        if (senderPhone.isBlank()) {
            return "Sender phone number is required"
        }
        if (!isValidPhoneNumber(senderPhone)) {
            return "Invalid sender phone number"
        }
        if (recipientName.isBlank()) {
            return "Recipient name is required"
        }
        if (recipientPhone.isBlank()) {
            return "Recipient phone number is required"
        }
        if (!isValidPhoneNumber(recipientPhone)) {
            return "Invalid recipient phone number"
        }
        return null
    }

    /**
     * Basic phone number validation.
     * Checks for 10 digits.
     */
    private fun isValidPhoneNumber(phone: String): Boolean {
        val cleaned = phone.replace(Regex("[^0-9]"), "")
        return cleaned.length == 10
    }

    /**
     * Load parcel delivery history.
     * Requirements: 5.3
     */
    fun loadParcelHistory() {
        viewModelScope.launch {
            _isLoading.value = true
            _error.value = null

            when (val result = parcelRepository.getParcelHistory()) {
                is Result.Success -> {
                    _parcelHistory.value = result.data
                }
                is Result.Error -> {
                    _error.value = result.message
                }
            }

            _isLoading.value = false
        }
    }

    /**
     * Get details of a specific parcel delivery.
     * Requirements: 5.4, 5.5
     * 
     * @param deliveryId ID of the parcel delivery
     */
    fun getParcelDetails(deliveryId: String) {
        viewModelScope.launch {
            _isLoading.value = true
            _error.value = null

            when (val result = parcelRepository.getParcelDetails(deliveryId)) {
                is Result.Success -> {
                    // Update active parcel if it matches
                    if (_activeParcel.value?.id == deliveryId) {
                        _activeParcel.value = result.data
                    }
                }
                is Result.Error -> {
                    _error.value = result.message
                }
            }

            _isLoading.value = false
        }
    }

    /**
     * Clear error state.
     */
    fun clearError() {
        _error.value = null
    }

    /**
     * Clear request success state.
     */
    fun clearRequestSuccess() {
        _requestSuccess.value = false
    }
}
