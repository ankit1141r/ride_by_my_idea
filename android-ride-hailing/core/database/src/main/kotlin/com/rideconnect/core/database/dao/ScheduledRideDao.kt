package com.rideconnect.core.database.dao

import androidx.room.*
import com.rideconnect.core.database.entity.ScheduledRideEntity
import kotlinx.coroutines.flow.Flow

@Dao
interface ScheduledRideDao {
    @Query("SELECT * FROM scheduled_rides WHERE rider_id = :riderId ORDER BY scheduled_time ASC")
    fun getScheduledRides(riderId: String): Flow<List<ScheduledRideEntity>>
    
    @Query("SELECT * FROM scheduled_rides WHERE id = :rideId")
    suspend fun getScheduledRideById(rideId: String): ScheduledRideEntity?
    
    @Query("SELECT * FROM scheduled_rides WHERE id = :rideId")
    fun observeScheduledRide(rideId: String): Flow<ScheduledRideEntity?>
    
    @Query("SELECT * FROM scheduled_rides WHERE rider_id = :riderId AND status = :status ORDER BY scheduled_time ASC")
    fun getScheduledRidesByStatus(riderId: String, status: String): Flow<List<ScheduledRideEntity>>
    
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertScheduledRide(ride: ScheduledRideEntity)
    
    @Update
    suspend fun updateScheduledRide(ride: ScheduledRideEntity)
    
    @Query("DELETE FROM scheduled_rides WHERE id = :rideId")
    suspend fun deleteScheduledRide(rideId: String)
    
    @Query("DELETE FROM scheduled_rides")
    suspend fun deleteAllScheduledRides()
    
    @Query("SELECT * FROM scheduled_rides ORDER BY scheduled_time ASC")
    suspend fun getAllScheduledRides(): List<ScheduledRideEntity>
    
    @Query("SELECT * FROM scheduled_rides ORDER BY scheduled_time ASC")
    fun observeScheduledRides(): Flow<List<ScheduledRideEntity>>
}
