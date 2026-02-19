package com.rideconnect.core.domain.model

data class Ride(
    val id: String,
    val riderId: String,
    val driverId: String?,
    val pickupLocation: Location,
    val dropoffLocation: Location,
    val status: RideStatus,
    val fare: Double?,
    val distance: Double?,
    val duration: Int?,
    val requestedAt: Long,
    val acceptedAt: Long?,
    val startedAt: Long?,
    val completedAt: Long?,
    val cancelledAt: Long?,
    val cancellationReason: String?,
    val driverDetails: DriverDetails? = null
)

enum class RideStatus {
    REQUESTED,
    SEARCHING,
    ACCEPTED,
    DRIVER_ARRIVING,
    ARRIVED,
    IN_PROGRESS,
    COMPLETED,
    CANCELLED
}

data class RideRequest(
    val pickupLocation: Location,
    val dropoffLocation: Location,
    val rideType: RideType = RideType.STANDARD
)

enum class RideType {
    STANDARD,
    PARCEL_DELIVERY,
    SCHEDULED
}

data class FareEstimate(
    val baseFare: Double,
    val distanceFare: Double,
    val timeFare: Double,
    val totalFare: Double,
    val distance: Double,
    val estimatedDuration: Int
)

data class DriverDetails(
    val id: String,
    val name: String,
    val phoneNumber: String,
    val profilePhotoUrl: String?,
    val rating: Double,
    val vehicleDetails: VehicleDetails?
)

data class CancelRideRequest(
    val reason: String
)
