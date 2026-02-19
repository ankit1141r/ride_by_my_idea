package com.rideconnect.core.data.repository

import com.rideconnect.core.common.result.Result
import com.rideconnect.core.data.local.TokenManager
import com.rideconnect.core.database.dao.EmergencyContactDao
import com.rideconnect.core.database.entity.EmergencyContactEntity
import com.rideconnect.core.domain.model.EmergencyContact
import com.rideconnect.core.domain.model.Location
import com.rideconnect.core.domain.model.RideShareLink
import com.rideconnect.core.domain.repository.EmergencyRepository
import com.rideconnect.core.network.api.EmergencyApi
import com.rideconnect.core.network.dto.EmergencyContactRequestDto
import com.rideconnect.core.network.dto.SOSRequestDto
import com.rideconnect.core.network.dto.ShareRideRequestDto
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map
import java.util.UUID
import javax.inject.Inject
import javax.inject.Singleton

/**
 * Implementation of EmergencyRepository.
 * Manages emergency contacts and SOS alerts with backend API and local database.
 * 
 * Requirements: 9.1, 9.2, 9.4, 9.7
 */
@Singleton
class EmergencyRepositoryImpl @Inject constructor(
    private val emergencyApi: EmergencyApi,
    private val emergencyContactDao: EmergencyContactDao,
    private val tokenManager: TokenManager
) : EmergencyRepository {
    
    /**
     * Trigger SOS alert with current location.
     * 
     * Requirements: 9.1, 9.2
     */
    override suspend fun triggerSOS(rideId: String, location: Location): Result<Unit> {
        return try {
            val request = SOSRequestDto(
                rideId = rideId,
                latitude = location.latitude,
                longitude = location.longitude,
                timestamp = System.currentTimeMillis()
            )
            
            val response = emergencyApi.triggerSOS(request)
            
            if (response.isSuccessful) {
                Result.Success(Unit)
            } else {
                Result.Error("Failed to trigger SOS: ${response.code()}")
            }
        } catch (e: Exception) {
            Result.Error(e.message ?: "Failed to trigger SOS")
        }
    }
    
    /**
     * Add an emergency contact.
     * 
     * Requirements: 9.7
     */
    override suspend fun addEmergencyContact(contact: EmergencyContact): Result<EmergencyContact> {
        return try {
            val currentUserId = tokenManager.getUserId() 
                ?: return Result.Error("User not authenticated")
            
            val request = EmergencyContactRequestDto(
                name = contact.name,
                phoneNumber = contact.phoneNumber,
                relationship = contact.relationship
            )
            
            val response = emergencyApi.addEmergencyContact(request)
            
            if (response.isSuccessful && response.body() != null) {
                val responseDto = response.body()!!
                
                // Store in local database
                val entity = EmergencyContactEntity(
                    id = responseDto.id,
                    userId = currentUserId,
                    name = responseDto.name,
                    phoneNumber = responseDto.phoneNumber,
                    relationship = responseDto.relationship
                )
                emergencyContactDao.insertContact(entity)
                
                Result.Success(entity.toDomainModel())
            } else {
                Result.Error("Failed to add emergency contact: ${response.code()}")
            }
        } catch (e: Exception) {
            Result.Error(e.message ?: "Failed to add emergency contact")
        }
    }
    
    /**
     * Remove an emergency contact.
     * 
     * Requirements: 9.7
     */
    override suspend fun removeEmergencyContact(contactId: String): Result<Unit> {
        return try {
            val response = emergencyApi.removeEmergencyContact(contactId)
            
            if (response.isSuccessful) {
                // Remove from local database
                emergencyContactDao.deleteContactById(contactId)
                Result.Success(Unit)
            } else {
                Result.Error("Failed to remove emergency contact: ${response.code()}")
            }
        } catch (e: Exception) {
            Result.Error(e.message ?: "Failed to remove emergency contact")
        }
    }
    
    /**
     * Get all emergency contacts.
     * 
     * Requirements: 9.7
     */
    override fun getEmergencyContacts(): Flow<List<EmergencyContact>> {
        val currentUserId = tokenManager.getUserId() ?: ""
        return emergencyContactDao.getEmergencyContacts(currentUserId).map { entities ->
            entities.map { it.toDomainModel() }
        }
    }
    
    /**
     * Share ride tracking link with emergency contacts.
     * 
     * Requirements: 9.4
     */
    override suspend fun shareRideWithContacts(
        rideId: String,
        contactIds: List<String>
    ): Result<RideShareLink> {
        return try {
            val request = ShareRideRequestDto(
                rideId = rideId,
                contactIds = contactIds
            )
            
            val response = emergencyApi.shareRide(request)
            
            if (response.isSuccessful && response.body() != null) {
                val responseDto = response.body()!!
                val shareLink = RideShareLink(
                    rideId = rideId,
                    shareUrl = responseDto.trackingLink,
                    expiresAt = System.currentTimeMillis() + (24 * 60 * 60 * 1000) // 24 hours
                )
                Result.Success(shareLink)
            } else {
                Result.Error("Failed to share ride: ${response.code()}")
            }
        } catch (e: Exception) {
            Result.Error(e.message ?: "Failed to share ride")
        }
    }
    
    /**
     * Convert database entity to domain model.
     */
    private fun EmergencyContactEntity.toDomainModel(): EmergencyContact {
        return EmergencyContact(
            id = id,
            name = name,
            phoneNumber = phoneNumber,
            relationship = relationship
        )
    }
}
