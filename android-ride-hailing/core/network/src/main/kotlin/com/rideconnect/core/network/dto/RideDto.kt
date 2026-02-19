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

data class ScheduledRideRequestDto(
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
    @SerializedName("scheduled_time")
    val scheduledTime: String
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
    val driver: DriverDto?,
    @SerializedName("rider")
    val rider: RiderDto?
)

data class ScheduledRideResponseDto(
    @SerializedName("id")
    val id: String,
    @SerializedName("rider_id")
    val riderId: String,
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
    @SerializedName("scheduled_time")
    val scheduledTime: String,
    @SerializedName("status")
    val status: String,
    @SerializedName("created_at")
    val createdAt: String
)

data class DriverDto(
    @SerializedName("id")
    val id: String,
    @SerializedName("name")
    val name: String,
    @SerializedName("phone_number")
    val phoneNumber: String,
    @SerializedName("profile_photo_url")
    val profilePhotoUrl: String?,
    @SerializedName("rating")
    val rating: Double,
    @SerializedName("vehicle_make")
    val vehicleMake: String?,
    @SerializedName("vehicle_model")
    val vehicleModel: String?,
    @SerializedName("vehicle_color")
    val vehicleColor: String?,
    @SerializedName("license_plate")
    val licensePlate: String?
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
