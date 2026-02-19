package com.rideconnect.core.database.dao

import androidx.room.*
import com.rideconnect.core.database.entity.PendingRatingEntity
import com.rideconnect.core.database.entity.RatingEntity
import kotlinx.coroutines.flow.Flow

/**
 * DAO for rating operations.
 * Requirements: 8.5, 8.6, 8.7
 */
@Dao
interface RatingDao {
    
    /**
     * Get all ratings for a user.
     * Requirements: 8.5, 8.6
     */
    @Query("SELECT * FROM ratings WHERE rated_user_id = :userId ORDER BY created_at DESC")
    fun getRatings(userId: String): Flow<List<RatingEntity>>
    
    /**
     * Insert a rating.
     * Requirements: 8.6
     */
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertRating(rating: RatingEntity)
    
    /**
     * Get all pending ratings.
     * Requirements: 8.7
     */
    @Query("SELECT * FROM pending_ratings ORDER BY created_at ASC")
    suspend fun getPendingRatings(): List<PendingRatingEntity>
    
    /**
     * Insert a pending rating.
     * Requirements: 8.7
     */
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertPendingRating(rating: PendingRatingEntity)
    
    /**
     * Delete a pending rating.
     * Requirements: 8.7
     */
    @Query("DELETE FROM pending_ratings WHERE ride_id = :rideId")
    suspend fun deletePendingRating(rideId: String)
    
    /**
     * Delete all pending ratings.
     * Requirements: 8.7
     */
    @Query("DELETE FROM pending_ratings")
    suspend fun deleteAllPendingRatings()
}
