package com.rideconnect.core.database.dao

import androidx.room.*
import com.rideconnect.core.database.entity.EmergencyContactEntity
import kotlinx.coroutines.flow.Flow

@Dao
interface EmergencyContactDao {
    @Query("SELECT * FROM emergency_contacts WHERE user_id = :userId")
    fun getEmergencyContacts(userId: String): Flow<List<EmergencyContactEntity>>
    
    @Query("SELECT * FROM emergency_contacts WHERE id = :contactId")
    suspend fun getEmergencyContactById(contactId: String): EmergencyContactEntity?
    
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertContact(contact: EmergencyContactEntity)
    
    @Update
    suspend fun updateContact(contact: EmergencyContactEntity)
    
    @Delete
    suspend fun deleteContact(contact: EmergencyContactEntity)
    
    @Query("DELETE FROM emergency_contacts WHERE id = :contactId")
    suspend fun deleteContactById(contactId: String)
    
    @Query("DELETE FROM emergency_contacts WHERE user_id = :userId")
    suspend fun deleteAllContactsForUser(userId: String)
    
    @Query("DELETE FROM emergency_contacts")
    suspend fun deleteAllContacts()
}
