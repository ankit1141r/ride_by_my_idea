package com.rideconnect.core.network.dto

import com.google.gson.annotations.SerializedName

/**
 * Rating DTO for API communication.
 * Requirements: 8.1, 8.2, 8.3
 */
data class RatingDto(
    @SerializedName("id") val id: String,
    @SerializedName("ride_id") val rideId: String,
    @SerializedName("rater_id") val raterId: String,
    @SerializedName("rated_user_id") val ratedUserId: String,
    @SerializedName("rating") val rating: Int,
    @SerializedName("review") val review: String?,
    @SerializedName("created_at") val createdAt: Long
)

/**
 * Rating request DTO.
 * Requirements: 8.1, 8.2, 8.3
 */
data class RatingRequestDto(
    @SerializedName("ride_id") val rideId: String,
    @SerializedName("rating") val rating: Int,
    @SerializedName("review") val review: String?
)

/**
 * Average rating response DTO.
 * Requirements: 8.5, 8.6
 */
data class AverageRatingDto(
    @SerializedName("user_id") val userId: String,
    @SerializedName("average_rating") val averageRating: Double,
    @SerializedName("total_ratings") val totalRatings: Int,
    @SerializedName("rating_breakdown") val ratingBreakdown: RatingBreakdownDto
)

/**
 * Rating breakdown DTO.
 * Requirements: 16.5
 */
data class RatingBreakdownDto(
    @SerializedName("five_stars") val fiveStars: Int,
    @SerializedName("four_stars") val fourStars: Int,
    @SerializedName("three_stars") val threeStars: Int,
    @SerializedName("two_stars") val twoStars: Int,
    @SerializedName("one_star") val oneStar: Int
)

/**
 * Rating response DTO.
 * Requirements: 8.1, 8.2
 */
data class RatingResponseDto(
    @SerializedName("id") val id: String,
    @SerializedName("ride_id") val rideId: String,
    @SerializedName("rater_id") val raterId: String,
    @SerializedName("rated_user_id") val ratedUserId: String,
    @SerializedName("rating") val rating: Int,
    @SerializedName("review") val review: String?,
    @SerializedName("created_at") val createdAt: String
)

/**
 * Average rating response DTO.
 * Requirements: 8.5, 8.6
 */
data class AverageRatingResponseDto(
    @SerializedName("user_id") val userId: String,
    @SerializedName("average_rating") val averageRating: Double,
    @SerializedName("total_ratings") val totalRatings: Int,
    @SerializedName("rating_breakdown") val ratingBreakdown: RatingBreakdownDto
)
