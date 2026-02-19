package com.rideconnect.core.database.dao

import androidx.room.*
import com.rideconnect.core.database.entity.ParcelDeliveryEntity
import kotlinx.coroutines.flow.Flow

@Dao
interface ParcelDeliveryDao {
    @Query("SELECT * FROM parcel_deliveries WHERE sender_id = :senderId ORDER BY requested_at DESC")
    fun getParcelHistory(senderId: String): Flow<List<ParcelDeliveryEntity>>
    
    @Query("SELECT * FROM parcel_deliveries WHERE driver_id = :driverId ORDER BY requested_at DESC")
    fun getDriverParcelHistory(driverId: String): Flow<List<ParcelDeliveryEntity>>
    
    @Query("SELECT * FROM parcel_deliveries WHERE id = :deliveryId")
    suspend fun getParcelDeliveryById(deliveryId: String): ParcelDeliveryEntity?
    
    @Query("SELECT * FROM parcel_deliveries WHERE id = :deliveryId")
    fun observeParcelDelivery(deliveryId: String): Flow<ParcelDeliveryEntity?>
    
    @Query("SELECT * FROM parcel_deliveries WHERE sender_id = :senderId AND status IN (:statuses) ORDER BY requested_at DESC LIMIT 1")
    fun getActiveParcelDelivery(senderId: String, statuses: List<String>): Flow<ParcelDeliveryEntity?>
    
    @Query("SELECT * FROM parcel_deliveries WHERE driver_id = :driverId AND status IN (:statuses) ORDER BY requested_at DESC LIMIT 1")
    fun getActiveDriverParcelDelivery(driverId: String, statuses: List<String>): Flow<ParcelDeliveryEntity?>
    
    @Query("SELECT * FROM parcel_deliveries WHERE status IN ('REQUESTED', 'ACCEPTED', 'PICKED_UP', 'IN_TRANSIT') ORDER BY requested_at DESC LIMIT 1")
    fun observeActiveParcelDelivery(): Flow<ParcelDeliveryEntity?>
    
    @Query("SELECT * FROM parcel_deliveries ORDER BY requested_at DESC")
    suspend fun getAllParcelDeliveries(): List<ParcelDeliveryEntity>
    
    @Query("UPDATE parcel_deliveries SET status = :status WHERE id = :deliveryId")
    suspend fun updateParcelStatus(deliveryId: String, status: String)
    
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertParcelDelivery(delivery: ParcelDeliveryEntity)
    
    @Update
    suspend fun updateParcelDelivery(delivery: ParcelDeliveryEntity)
    
    @Query("DELETE FROM parcel_deliveries WHERE id = :deliveryId")
    suspend fun deleteParcelDelivery(deliveryId: String)
    
    @Query("DELETE FROM parcel_deliveries")
    suspend fun deleteAllParcelDeliveries()
}
