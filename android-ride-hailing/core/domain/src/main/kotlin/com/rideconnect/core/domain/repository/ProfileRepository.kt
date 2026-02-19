package com.rideconnect.core.domain.repository

import com.rideconnect.core.common.result.Result
import com.rideconnect.core.domain.model.EmergencyContact
import com.rideconnect.core.domain.model.ProfileUpdateRequest
import com.rideconnect.core.domain.model.User
import com.rideconnect.core.domain.model.VehicleDetails
import java.io.File

interface ProfileRepository {
    
    suspend fun updateProfile(request: ProfileUpdateRequest): Result<User>
    
    suspend fun uploadProfilePhoto(photoFile: File): Result<String>
    
    suspend fun getProfile(): Result<User>
    
    suspend fun updateVehicleDetails(vehicleDetails: VehicleDetails, licenseNumber: String): Result<VehicleDetails>
    
    suspend fun getVehicleDetails(): Result<VehicleDetails>
    
    suspend fun getEmergencyContacts(): Result<List<EmergencyContact>>
    
    suspend fun addEmergencyContact(contact: EmergencyContact): Result<EmergencyContact>
    
    suspend fun removeEmergencyContact(contactId: String): Result<Unit>
}
