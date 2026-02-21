package com.rideconnect.core.database.dao

import androidx.room.*
import com.rideconnect.core.database.entity.EarningsEntity
import kotlinx.coroutines.flow.Flow

/**
 * DAO for earnings data operations.
 * Requirements: 14.5, 14.6, 14.7
 */
@Dao
interface EarningsDao {
    
    @Query("SELECT * FROM earnings WHERE driver_id = :driverId AND date BETWEEN :startDate AND :endDate ORDER BY date DESC")
    fun getEarningsByDateRange(driverId: String, startDate: Long, endDate: Long): Flow<List<EarningsEntity>>
    
    @Query("SELECT * FROM earnings WHERE driver_id = :driverId ORDER BY date DESC")
    fun getAllEarnings(driverId: String): Flow<List<EarningsEntity>>
    
    @Query("SELECT * FROM earnings WHERE driver_id = :driverId AND is_pending = 1")
    fun getPendingEarnings(driverId: String): Flow<List<EarningsEntity>>
    
    @Query("SELECT * FROM earnings WHERE synced = 0")
    suspend fun getUnsyncedEarnings(): List<EarningsEntity>
    
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertEarning(earning: EarningsEntity)
    
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertEarnings(earnings: List<EarningsEntity>)
    
    @Update
    suspend fun updateEarning(earning: EarningsEntity)
    
    @Query("UPDATE earnings SET synced = 1 WHERE id = :earningId")
    suspend fun markAsSynced(earningId: String)
    
    @Query("DELETE FROM earnings WHERE driver_id = :driverId")
    suspend fun deleteAllEarnings(driverId: String)
    
    @Query("SELECT SUM(fare) FROM earnings WHERE driver_id = :driverId AND date BETWEEN :startDate AND :endDate")
    suspend fun getTotalEarnings(driverId: String, startDate: Long, endDate: Long): Double?
    
    @Query("SELECT COUNT(*) FROM earnings WHERE driver_id = :driverId AND date BETWEEN :startDate AND :endDate")
    suspend fun getTotalRides(driverId: String, startDate: Long, endDate: Long): Int
}
