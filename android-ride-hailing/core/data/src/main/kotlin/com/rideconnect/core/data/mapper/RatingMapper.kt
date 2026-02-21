package com.rideconnect.core.data.mapper

import com.rideconnect.core.domain.model.*
import com.rideconnect.core.network.dto.*
import com.rideconnect.core.database.entity.RatingEntity
import java.time.Instant
import java.time.format.DateTimeFormatter

object RatingMapper {
    
    fun toDto(request: RatingRequest): RatingRequestDto {
        return RatingRequestDto(
            rideId = request.rideId,
            rating = request.rating,
            review = request.review
        )
    }
    
    fun toRating(dto: RatingResponseDto): Rating {
        return Rating(
            id = dto.id,
            rideId = dto.rideId,
            raterId = dto.raterId,
            ratedUserId = dto.ratedUserId,
            rating = dto.rating,
            review = dto.review,
            createdAt = parseTimestamp(dto.createdAt)
        )
    }
    
    fun toEntity(rating: Rating): RatingEntity {
        return RatingEntity(
            id = rating.id,
            rideId = rating.rideId,
            raterId = rating.raterId,
            ratedUserId = rating.ratedUserId,
            rating = rating.rating,
            review = rating.review,
            createdAt = rating.createdAt
        )
    }
    
    fun toAverageRating(dto: AverageRatingResponseDto): AverageRating {
        return AverageRating(
            userId = dto.userId,
            averageRating = dto.averageRating,
            totalRatings = dto.totalRatings,
            ratingBreakdown = RatingBreakdown(
                fiveStars = dto.ratingBreakdown.fiveStars,
                fourStars = dto.ratingBreakdown.fourStars,
                threeStars = dto.ratingBreakdown.threeStars,
                twoStars = dto.ratingBreakdown.twoStars,
                oneStar = dto.ratingBreakdown.oneStar
            )
        )
    }
    
    private fun parseTimestamp(timestamp: String): Long {
        return try {
            Instant.from(DateTimeFormatter.ISO_INSTANT.parse(timestamp)).toEpochMilli()
        } catch (e: Exception) {
            System.currentTimeMillis()
        }
    }
}
