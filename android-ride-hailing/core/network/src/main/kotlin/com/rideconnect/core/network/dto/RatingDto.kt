package com.rideconnect.core.network.dto

import com.google.gson.annotations.SerializedName

data class RatingRequestDto(
    @SerializedName("ride_id")
    val rideId: String,
    @SerializedName("rating")
    val rating: Int,
    @SerializedName("review")
    val review: String?
)

data class RatingResponseDto(
    @SerializedName("id")
    val id: String,
    @SerializedName("ride_id")
    val rideId: String,
    @SerializedName("rater_id")
    val raterId: String,
    @SerializedName("rated_user_id")
    val ratedUserId: String,
    @SerializedName("rating")
    val rating: Int,
    @SerializedName("review")
    val review: String?,
    @SerializedName("created_at")
    val createdAt: String
)

data class AverageRatingResponseDto(
    @SerializedName("user_id")
    val userId: String,
    @SerializedName("average_rating")
    val averageRating: Double,
    @SerializedName("total_ratings")
    val totalRatings: Int
)
