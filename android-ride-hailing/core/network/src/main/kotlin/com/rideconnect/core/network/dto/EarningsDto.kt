package com.rideconnect.core.network.dto

import com.google.gson.annotations.SerializedName

/**
 * DTO for earnings response from backend.
 * Requirements: 14.1, 14.2, 14.3, 14.4
 */
data class EarningsResponseDto(
    @SerializedName("total_earnings")
    val totalEarnings: Double,
    
    @SerializedName("total_rides")
    val totalRides: Int,
    
    @SerializedName("average_fare")
    val averageFare: Double,
    
    @SerializedName("pending_earnings")
    val pendingEarnings: Double,
    
    @SerializedName("rides")
    val rides: List<EarningsRideDto>
)

/**
 * DTO for individual ride earnings.
 * Requirements: 14.2, 14.6
 */
data class EarningsRideDto(
    @SerializedName("ride_id")
    val rideId: String,
    
    @SerializedName("date")
    val date: String, // ISO 8601 format: YYYY-MM-DD
    
    @SerializedName("fare")
    val fare: Double,
    
    @SerializedName("pickup_address")
    val pickupAddress: String,
    
    @SerializedName("dropoff_address")
    val dropoffAddress: String,
    
    @SerializedName("distance")
    val distance: Double?,
    
    @SerializedName("duration")
    val duration: Int?
)
