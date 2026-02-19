package com.rideconnect.core.domain.repository

import com.rideconnect.core.common.result.Result
import com.rideconnect.core.domain.model.EmergencyContact
import com.rideconnect.core.domain.model.Location
import com.rideconnect.core.domain.model.RideShareLink
import kotlinx.coroutines.flow.Flow

/**
 * Repository interface for emergency operations.
 * Handles SOS alerts, emergency contacts, and ride sharing.
 * 
 * Requirements: 9.1, 9.2, 9.4, 9.7
 */
interface EmergencyRepository {
    /**
     * Trigger SOS alert with current location.
     * Sends alert to backend and emergency contacts.
     * 
     * Requirements: 9.1, 9.2
     */
    suspend fun triggerSOS(rideId: String, location: Location): Result<Unit>
    
    /**
     * Add an emergency contact.
     * 
     * Requirements: 9.7
     */
    suspend fun addEmergencyContact(contact: EmergencyContact): Result<EmergencyContact>
    
    /**
     * Remove an emergency contact.
     * 
     * Requirements: 9.7
     */
    suspend fun removeEmergencyContact(contactId: String): Result<Unit>
    
    /**
     * Get all emergency contacts.
     * Returns a Flow that emits updated contact lists.
     * 
     * Requirements: 9.7
     */
    fun getEmergencyContacts(): Flow<List<EmergencyContact>>
    
    /**
     * Share ride tracking link with emergency contacts.
     * 
     * Requirements: 9.4
     */
    suspend fun shareRideWithContacts(rideId: String, contactIds: List<String>): Result<RideShareLink>
}
