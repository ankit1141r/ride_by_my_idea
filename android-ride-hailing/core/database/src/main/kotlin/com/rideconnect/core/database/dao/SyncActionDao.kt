package com.rideconnect.core.database.dao

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import com.rideconnect.core.database.entity.SyncActionEntity

/**
 * DAO for sync action operations
 */
@Dao
interface SyncActionDao {
    
    /**
     * Inserts a new sync action
     */
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertAction(action: SyncActionEntity): Long
    
    /**
     * Gets all pending sync actions ordered by timestamp
     */
    @Query("SELECT * FROM sync_actions WHERE status = 'PENDING' ORDER BY timestamp ASC")
    suspend fun getPendingActions(): List<SyncActionEntity>
    
    /**
     * Updates the status of a sync action
     */
    @Query("UPDATE sync_actions SET status = :status WHERE id = :actionId")
    suspend fun updateActionStatus(actionId: Long, status: String)
    
    /**
     * Updates the retry count of a sync action
     */
    @Query("UPDATE sync_actions SET retryCount = :retryCount WHERE id = :actionId")
    suspend fun updateRetryCount(actionId: Long, retryCount: Int)
    
    /**
     * Deletes all completed sync actions
     */
    @Query("DELETE FROM sync_actions WHERE status = 'COMPLETED'")
    suspend fun deleteCompletedActions()
    
    /**
     * Deletes all failed sync actions
     */
    @Query("DELETE FROM sync_actions WHERE status = 'FAILED'")
    suspend fun deleteFailedActions()
    
    /**
     * Gets count of pending sync actions
     */
    @Query("SELECT COUNT(*) FROM sync_actions WHERE status = 'PENDING'")
    suspend fun getPendingActionCount(): Int
    
    /**
     * Gets all sync actions (for debugging)
     */
    @Query("SELECT * FROM sync_actions ORDER BY timestamp DESC")
    suspend fun getAllActions(): List<SyncActionEntity>
}
