package com.rideconnect.core.domain.model

/**
 * Rating data model.
 * Requirements: 8.1, 8.2, 8.3
 */
data class Rating(
    val id: String,
    val rideId: String,
    val raterId: String,
    val ratedUserId: String,
    val rating: Int, // 1-5 stars
    val review: String?,
    val createdAt: Long
)

/**
 * Request to submit a rating.
 * Requirements: 8.1, 8.2, 8.3
 */
data class RatingRequest(
    val rideId: String,
    val rating: Int, // 1-5 stars
    val review: String? = null
) {
    init {
        require(rating in 1..5) { "Rating must be between 1 and 5" }
        review?.let {
            require(it.length <= 500) { "Review must not exceed 500 characters" }
        }
    }
}

/**
 * Average rating response.
 * Requirements: 8.5, 8.6
 */
data class AverageRating(
    val userId: String,
    val averageRating: Double,
    val totalRatings: Int,
    val ratingBreakdown: RatingBreakdown
)

/**
 * Breakdown of ratings by star count.
 * Requirements: 16.5
 */
data class RatingBreakdown(
    val fiveStars: Int,
    val fourStars: Int,
    val threeStars: Int,
    val twoStars: Int,
    val oneStar: Int
)
