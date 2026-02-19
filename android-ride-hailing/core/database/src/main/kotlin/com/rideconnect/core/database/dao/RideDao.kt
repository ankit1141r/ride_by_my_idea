package com.rideconnect.core.database.dao

import androidx.room.*
import com.rideconnect.core.database.entity.RideEntity
import kotlinx.coroutines.flow.Flow

@Dao
interface RideDao {
    @Query("SELECT * FROM rides WHERE rider_id = :userId ORDER BY requested_at DESC")
    fun getRideHistory(userId: String): Flow<List<RideEntity>>
    
    @Query("SELECT * FROM rides WHERE driver_id = :driverId ORDER BY requested_at DESC")
    fun getDriverRideHistory(driverId: String): Flow<List<RideEntity>>
    
    @Query("SELECT * FROM rides WHERE id = :rideId")
    suspend fun getRideById(rideId: String): RideEntity?
    
    @Query("SELECT * FROM rides WHERE id = :rideId")
    fun observeRide(rideId: String): Flow<RideEntity?>
    
    @Query("SELECT * FROM rides WHERE rider_id = :userId AND status IN (:statuses) ORDER BY requested_at DESC LIMIT 1")
    fun getActiveRide(userId: String, statuses: List<String>): Flow<RideEntity?>
    
    @Query("SELECT * FROM rides WHERE driver_id = :driverId AND status IN (:statuses) ORDER BY requested_at DESC LIMIT 1")
    fun getActiveDriverRide(driverId: String, statuses: List<String>): Flow<RideEntity?>
    
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertRide(ride: RideEntity)
    
    @Update
    suspend fun updateRide(ride: RideEntity)
    
    @Query("DELETE FROM rides WHERE id = :rideId")
    suspend fun deleteRide(rideId: String)
    
    @Query("DELETE FROM rides")
    suspend fun deleteAllRides()
    
    @Query("SELECT * FROM rides WHERE rider_id = :userId AND requested_at >= :startTime AND requested_at <= :endTime ORDER BY requested_at DESC")
    fun getRidesByDateRange(userId: String, startTime: Long, endTime: Long): Flow<List<RideEntity>>
}
