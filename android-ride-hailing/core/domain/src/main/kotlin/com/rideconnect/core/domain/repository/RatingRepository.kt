package com.rideconnect.core.domain.repository

import com.rideconnect.core.common.result.Result
import com.rideconnect.core.domain.model.AverageRating
import com.rideconnect.core.domain.model.Rating
import com.rideconnect.core.domain.model.RatingRequest
import kotlinx.coroutines.flow.Flow

/**
 * Repository interface for rating operations.
 * Requirements: 8.3, 8.5, 8.6, 8.7
 */
interface RatingRepository {
    
    /**
     * Submit a rating for a ride.
     * Requirements: 8.3
     */
    suspend fun submitRating(request: RatingRequest): Result<Unit>
    
    /**
     * Get ratings for a user.
     * Requirements: 8.5, 8.6
     */
    suspend fun getRatings(userId: String): Result<List<Rating>>
    
    /**
     * Get average rating for a user.
     * Requirements: 8.5, 8.6
     */
    suspend fun getAverageRating(userId: String): Result<AverageRating>
    
    /**
     * Observe ratings from local database.
     * Requirements: 8.6
     */
    fun observeRatings(userId: String): Flow<List<Rating>>
    
    /**
     * Get pending ratings that need to be synced.
     * Requirements: 8.7
     */
    suspend fun getPendingRatings(): List<RatingRequest>
    
    /**
     * Queue rating for offline sync.
     * Requirements: 8.7
     */
    suspend fun queueRatingForSync(request: RatingRequest)
}
