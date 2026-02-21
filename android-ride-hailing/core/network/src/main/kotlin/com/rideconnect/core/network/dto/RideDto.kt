package com.rideconnect.core.network.dto

import com.google.gson.annotations.SerializedName

// Request DTOs
data class RideRequestDto(
    @SerializedName("pickup_latitude")
    val pickupLatitude: Double,
    @SerializedName("pickup_longitude")
    val pickupLongitude: Double,
    @SerializedName("pickup_address")
    val pickupAddress: String?,
    @SerializedName("dropoff_latitude")
    val dropoffLatitude: Double,
    @SerializedName("dropoff_longitude")
    val dropoffLongitude: Double,
    @SerializedName("dropoff_address")
    val dropoffAddress: String?
)

data class CancelRideRequestDto(
    @SerializedName("reason")
    val reason: String
)

data class RejectRideRequestDto(
    @SerializedName("reason")
    val reason: String
)

// Response DTOs
data class RideResponseDto(
    @SerializedName("id")
    val id: String,
    @SerializedName("rider_id")
    val riderId: String,
    @SerializedName("driver_id")
    val driverId: String?,
    @SerializedName("pickup_latitude")
    val pickupLatitude: Double,
    @SerializedName("pickup_longitude")
    val pickupLongitude: Double,
    @SerializedName("pickup_address")
    val pickupAddress: String?,
    @SerializedName("dropoff_latitude")
    val dropoffLatitude: Double,
    @SerializedName("dropoff_longitude")
    val dropoffLongitude: Double,
    @SerializedName("dropoff_address")
    val dropoffAddress: String?,
    @SerializedName("status")
    val status: String,
    @SerializedName("fare")
    val fare: Double?,
    @SerializedName("distance")
    val distance: Double?,
    @SerializedName("duration")
    val duration: Int?,
    @SerializedName("requested_at")
    val requestedAt: String,
    @SerializedName("accepted_at")
    val acceptedAt: String?,
    @SerializedName("started_at")
    val startedAt: String?,
    @SerializedName("completed_at")
    val completedAt: String?,
    @SerializedName("cancelled_at")
    val cancelledAt: String?,
    @SerializedName("cancellation_reason")
    val cancellationReason: String?,
    @SerializedName("driver")
    val driver: DriverDetailsDto?,
    @SerializedName("rider")
    val rider: RiderDto?
)

data class RiderDto(
    @SerializedName("id")
    val id: String,
    @SerializedName("name")
    val name: String,
    @SerializedName("phone_number")
    val phoneNumber: String,
    @SerializedName("profile_photo_url")
    val profilePhotoUrl: String?,
    @SerializedName("rating")
    val rating: Double
)

data class FareEstimateResponseDto(
    @SerializedName("base_fare")
    val baseFare: Double,
    @SerializedName("distance_fare")
    val distanceFare: Double,
    @SerializedName("time_fare")
    val timeFare: Double,
    @SerializedName("total_fare")
    val totalFare: Double,
    @SerializedName("distance")
    val distance: Double,
    @SerializedName("estimated_duration")
    val estimatedDuration: Int
)
