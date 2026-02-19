package com.rideconnect.core.network.dto

import com.google.gson.annotations.SerializedName

data class AvailabilityRequestDto(
    @SerializedName("is_available")
    val isAvailable: Boolean
)

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

data class EarningsRideDto(
    @SerializedName("id")
    val id: String,
    @SerializedName("date")
    val date: String,
    @SerializedName("fare")
    val fare: Double,
    @SerializedName("pickup_address")
    val pickupAddress: String?,
    @SerializedName("dropoff_address")
    val dropoffAddress: String?
)
