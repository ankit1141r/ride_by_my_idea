package com.rideconnect.core.network.dto

import com.google.gson.annotations.SerializedName

/**
 * DTOs for scheduled ride API communication.
 * 
 * Requirements: 4.1, 4.4
 */
data class ScheduledRideRequestDto(
    @SerializedName("pickup_location")
    val pickupLocation: LocationDto,
    @SerializedName("dropoff_location")
    val dropoffLocation: LocationDto,
    @SerializedName("scheduled_time")
    val scheduledTime: String // ISO 8601 format
)

data class ScheduledRideResponseDto(
    @SerializedName("id")
    val id: String,
    @SerializedName("rider_id")
    val riderId: String,
    @SerializedName("pickup_location")
    val pickupLocation: LocationDto,
    @SerializedName("dropoff_location")
    val dropoffLocation: LocationDto,
    @SerializedName("scheduled_time")
    val scheduledTime: String, // ISO 8601 format
    @SerializedName("status")
    val status: String,
    @SerializedName("fare")
    val fare: Double?,
    @SerializedName("distance")
    val distance: Double?,
    @SerializedName("created_at")
    val createdAt: String // ISO 8601 format
)

data class CancelScheduledRideRequestDto(
    @SerializedName("reason")
    val reason: String
)

data class LocationDto(
    @SerializedName("latitude")
    val latitude: Double,
    @SerializedName("longitude")
    val longitude: Double,
    @SerializedName("address")
    val address: String?
)
