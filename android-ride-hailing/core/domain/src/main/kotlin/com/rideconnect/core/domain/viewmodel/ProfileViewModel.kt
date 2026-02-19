package com.rideconnect.core.domain.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.rideconnect.core.common.result.Result
import com.rideconnect.core.domain.model.EmergencyContact
import com.rideconnect.core.domain.model.ProfileUpdateRequest
import com.rideconnect.core.domain.model.User
import com.rideconnect.core.domain.model.VehicleDetails
import com.rideconnect.core.domain.repository.ProfileRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import java.io.File
import javax.inject.Inject

@HiltViewModel
class ProfileViewModel @Inject constructor(
    private val profileRepository: ProfileRepository
) : ViewModel() {
    
    private val _profileState = MutableStateFlow<ProfileState>(ProfileState.Idle)
    val profileState: StateFlow<ProfileState> = _profileState.asStateFlow()
    
    private val _user = MutableStateFlow<User?>(null)
    val user: StateFlow<User?> = _user.asStateFlow()
    
    private val _vehicleDetails = MutableStateFlow<VehicleDetails?>(null)
    val vehicleDetails: StateFlow<VehicleDetails?> = _vehicleDetails.asStateFlow()
    
    private val _emergencyContacts = MutableStateFlow<List<EmergencyContact>>(emptyList())
    val emergencyContacts: StateFlow<List<EmergencyContact>> = _emergencyContacts.asStateFlow()
    
    private val _photoUploadState = MutableStateFlow<PhotoUploadState>(PhotoUploadState.Idle)
    val photoUploadState: StateFlow<PhotoUploadState> = _photoUploadState.asStateFlow()
    
    fun loadProfile() {
        viewModelScope.launch {
            _profileState.value = ProfileState.Loading
            
            when (val result = profileRepository.getProfile()) {
                is Result.Success -> {
                    _user.value = result.data
                    _profileState.value = ProfileState.Success
                }
                is Result.Error -> {
                    _profileState.value = ProfileState.Error(
                        result.exception.message ?: "Failed to load profile"
                    )
                }
            }
        }
    }
    
    fun updateProfile(name: String?, email: String?) {
        viewModelScope.launch {
            _profileState.value = ProfileState.Loading
            
            val request = ProfileUpdateRequest(
                name = name,
                email = email
            )
            
            when (val result = profileRepository.updateProfile(request)) {
                is Result.Success -> {
                    _user.value = result.data
                    _profileState.value = ProfileState.Success
                }
                is Result.Error -> {
                    _profileState.value = ProfileState.Error(
                        result.exception.message ?: "Failed to update profile"
                    )
                }
            }
        }
    }
    
    fun uploadProfilePhoto(photoFile: File) {
        viewModelScope.launch {
            _photoUploadState.value = PhotoUploadState.Uploading
            
            when (val result = profileRepository.uploadProfilePhoto(photoFile)) {
                is Result.Success -> {
                    _photoUploadState.value = PhotoUploadState.Success(result.data)
                    
                    // Update profile with new photo URL
                    val request = ProfileUpdateRequest(profilePhotoUrl = result.data)
                    profileRepository.updateProfile(request)
                    
                    // Reload profile to get updated data
                    loadProfile()
                }
                is Result.Error -> {
                    _photoUploadState.value = PhotoUploadState.Error(
                        result.exception.message ?: "Failed to upload photo"
                    )
                }
            }
        }
    }
    
    fun resetPhotoUploadState() {
        _photoUploadState.value = PhotoUploadState.Idle
    }
    
    fun loadVehicleDetails() {
        viewModelScope.launch {
            when (val result = profileRepository.getVehicleDetails()) {
                is Result.Success -> {
                    _vehicleDetails.value = result.data
                }
                is Result.Error -> {
                    _profileState.value = ProfileState.Error(
                        result.exception.message ?: "Failed to load vehicle details"
                    )
                }
            }
        }
    }
    
    fun updateVehicleDetails(vehicleDetails: VehicleDetails, licenseNumber: String) {
        viewModelScope.launch {
            _profileState.value = ProfileState.Loading
            
            when (val result = profileRepository.updateVehicleDetails(vehicleDetails, licenseNumber)) {
                is Result.Success -> {
                    _vehicleDetails.value = result.data
                    _profileState.value = ProfileState.Success
                }
                is Result.Error -> {
                    _profileState.value = ProfileState.Error(
                        result.exception.message ?: "Failed to update vehicle details"
                    )
                }
            }
        }
    }
    
    fun loadEmergencyContacts() {
        viewModelScope.launch {
            when (val result = profileRepository.getEmergencyContacts()) {
                is Result.Success -> {
                    _emergencyContacts.value = result.data
                }
                is Result.Error -> {
                    _profileState.value = ProfileState.Error(
                        result.exception.message ?: "Failed to load emergency contacts"
                    )
                }
            }
        }
    }
    
    fun addEmergencyContact(name: String, phoneNumber: String, relationship: String?) {
        viewModelScope.launch {
            _profileState.value = ProfileState.Loading
            
            val contact = EmergencyContact(
                id = "", // Will be assigned by backend
                name = name,
                phoneNumber = phoneNumber,
                relationship = relationship
            )
            
            when (val result = profileRepository.addEmergencyContact(contact)) {
                is Result.Success -> {
                    // Reload contacts list
                    loadEmergencyContacts()
                    _profileState.value = ProfileState.Success
                }
                is Result.Error -> {
                    _profileState.value = ProfileState.Error(
                        result.exception.message ?: "Failed to add emergency contact"
                    )
                }
            }
        }
    }
    
    fun removeEmergencyContact(contactId: String) {
        viewModelScope.launch {
            _profileState.value = ProfileState.Loading
            
            when (val result = profileRepository.removeEmergencyContact(contactId)) {
                is Result.Success -> {
                    // Reload contacts list
                    loadEmergencyContacts()
                    _profileState.value = ProfileState.Success
                }
                is Result.Error -> {
                    _profileState.value = ProfileState.Error(
                        result.exception.message ?: "Failed to remove emergency contact"
                    )
                }
            }
        }
    }
    
    fun resetState() {
        _profileState.value = ProfileState.Idle
    }
}

sealed class ProfileState {
    object Idle : ProfileState()
    object Loading : ProfileState()
    object Success : ProfileState()
    data class Error(val message: String) : ProfileState()
}

sealed class PhotoUploadState {
    object Idle : PhotoUploadState()
    object Uploading : PhotoUploadState()
    data class Success(val photoUrl: String) : PhotoUploadState()
    data class Error(val message: String) : PhotoUploadState()
}
