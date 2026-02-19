package com.rideconnect.core.domain.model

/**
 * Scheduled ride domain models.
 * 
 * Requirements: 4.1, 4.4
 */
data class ScheduledRide(
    val id: String,
    val riderId: String,
    val pickupLocation: Location,
    val dropoffLocation: Location,
    val scheduledTime: Long, // Unix timestamp in milliseconds
    val status: ScheduledRideStatus,
    val fare: Double?,
    val distance: Double?,
    val createdAt: Long,
    val cancelledAt: Long? = null,
    val cancellationReason: String? = null
)

enum class ScheduledRideStatus {
    SCHEDULED,      // Ride is scheduled for future
    CONFIRMED,      // Driver assigned (30 min before scheduled time)
    IN_PROGRESS,    // Ride has started
    COMPLETED,      // Ride completed successfully
    CANCELLED       // Ride was cancelled
}

data class ScheduledRideRequest(
    val pickupLocation: Location,
    val dropoffLocation: Location,
    val scheduledTime: Long // Unix timestamp in milliseconds
)

data class ScheduledRideResponse(
    val id: String,
    val riderId: String,
    val pickupLocation: Location,
    val dropoffLocation: Location,
    val scheduledTime: Long,
    val status: String,
    val fare: Double?,
    val distance: Double?,
    val createdAt: Long
)
