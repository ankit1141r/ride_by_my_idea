package com.rideconnect.core.data.mapper

import com.rideconnect.core.domain.model.AverageRating
import com.rideconnect.core.domain.model.Rating
import com.rideconnect.core.domain.model.RatingBreakdown
import com.rideconnect.core.domain.model.RatingRequest
import com.rideconnect.core.network.dto.AverageRatingDto
import com.rideconnect.core.network.dto.RatingBreakdownDto
import com.rideconnect.core.network.dto.RatingDto
import com.rideconnect.core.network.dto.RatingRequestDto

/**
 * Mapper functions for Rating domain models and DTOs.
 * Requirements: 8.1, 8.2, 8.3, 8.5, 8.6
 */

/**
 * Convert RatingDto to Rating domain model.
 */
fun RatingDto.toRating(): Rating {
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

/**
 * Convert RatingRequest to RatingRequestDto.
 */
fun RatingRequest.toDto(): RatingRequestDto {
    return RatingRequestDto(
        rideId = rideId,
        rating = rating,
        review = review
    )
}

/**
 * Convert AverageRatingDto to AverageRating domain model.
 */
fun AverageRatingDto.toAverageRating(): AverageRating {
    return AverageRating(
        userId = userId,
        averageRating = averageRating,
        totalRatings = totalRatings,
        ratingBreakdown = ratingBreakdown.toRatingBreakdown()
    )
}

/**
 * Convert RatingBreakdownDto to RatingBreakdown domain model.
 */
fun RatingBreakdownDto.toRatingBreakdown(): RatingBreakdown {
    return RatingBreakdown(
        fiveStars = fiveStars,
        fourStars = fourStars,
        threeStars = threeStars,
        twoStars = twoStars,
        oneStar = oneStar
    )
}
