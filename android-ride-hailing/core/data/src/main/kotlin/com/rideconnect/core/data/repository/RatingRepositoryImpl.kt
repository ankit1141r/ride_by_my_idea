package com.rideconnect.core.data.repository

import com.rideconnect.core.common.network.safeApiCall
import com.rideconnect.core.common.result.Result
import com.rideconnect.core.data.mapper.toAverageRating
import com.rideconnect.core.data.mapper.toDto
import com.rideconnect.core.data.mapper.toRating
import com.rideconnect.core.database.dao.RatingDao
import com.rideconnect.core.database.entity.PendingRatingEntity
import com.rideconnect.core.database.entity.RatingEntity
import com.rideconnect.core.domain.model.AverageRating
import com.rideconnect.core.domain.model.Rating
import com.rideconnect.core.domain.model.RatingRequest
import com.rideconnect.core.domain.repository.RatingRepository
import com.rideconnect.core.network.api.RatingApi
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map
import javax.inject.Inject
import javax.inject.Singleton

/**
 * Implementation of RatingRepository.
 * Requirements: 8.3, 8.5, 8.6, 8.7
 */
@Singleton
class RatingRepositoryImpl @Inject constructor(
    private val ratingApi: RatingApi,
    private val ratingDao: RatingDao
) : RatingRepository {
    
    /**
     * Submit a rating for a ride.
     * Requirements: 8.3
     */
    override suspend fun submitRating(request: RatingRequest): Result<Unit> {
        return safeApiCall {
            ratingApi.submitRating(request.toDto())
        }.map {
            // Remove from pending queue if it was queued
            ratingDao.deletePendingRating(request.rideId)
        }
    }
    
    /**
     * Get ratings for a user.
     * Requirements: 8.5, 8.6
     */
    override suspend fun getRatings(userId: String): Result<List<Rating>> {
        return safeApiCall {
            ratingApi.getRatings(userId)
        }.map { ratingDtos ->
            val ratings = ratingDtos.map { it.toRating() }
            
            // Store ratings in local database
            ratings.forEach { rating ->
                ratingDao.insertRating(rating.toEntity())
            }
            
            ratings
        }
    }
    
    /**
     * Get average rating for a user.
     * Requirements: 8.5, 8.6
     */
    override suspend fun getAverageRating(userId: String): Result<AverageRating> {
        return safeApiCall {
            ratingApi.getAverageRating(userId)
        }.map { averageRatingDto ->
            averageRatingDto.toAverageRating()
        }
    }
    
    /**
     * Observe ratings from local database.
     * Requirements: 8.6
     */
    override fun observeRatings(userId: String): Flow<List<Rating>> {
        return ratingDao.getRatings(userId)
            .map { entities ->
                entities.map { it.toRating() }
            }
    }
    
    /**
     * Get pending ratings that need to be synced.
     * Requirements: 8.7
     */
    override suspend fun getPendingRatings(): List<RatingRequest> {
        return ratingDao.getPendingRatings()
            .map { entity ->
                RatingRequest(
                    rideId = entity.rideId,
                    rating = entity.rating,
                    review = entity.review
                )
            }
    }
    
    /**
     * Queue rating for offline sync.
     * Requirements: 8.7
     */
    override suspend fun queueRatingForSync(request: RatingRequest) {
        val entity = PendingRatingEntity(
            rideId = request.rideId,
            rating = request.rating,
            review = request.review,
            createdAt = System.currentTimeMillis()
        )
        ratingDao.insertPendingRating(entity)
    }
}

/**
 * Extension function to convert Rating to RatingEntity
 */
private fun Rating.toEntity(): RatingEntity {
    return RatingEntity(
        id = id,
        rideId = rideId,
        raterId = raterId,
        ratedUserId = ratedUserId,
        rating = rating,
        review = review,
        createdAt = createdAt
    )
}

/**
 * Extension function to convert RatingEntity to Rating
 */
private fun RatingEntity.toRating(): Rating {
    return Rating(
        id = id,
        rideId = rideId,
        raterId = raterId,
        ratedUserId = ratedUserId,
        rating = rating,
        review = review,
        createdAt = createdAt
    )
}
