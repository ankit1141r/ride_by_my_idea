package com.rideconnect.core.domain.model

import java.time.LocalDateTime

/**
 * Driver model representing a driver in the system.
 * Requirements: 11.1, 11.2, 11.3
 */
data class Driver(
    val id: String,
    val user: User,
    val vehicleDetails: VehicleDetails,
    val licenseNumber: String,
    val isAvailable: Boolean,
    val currentLocation: Location?,
    val acceptsParcelDelivery: Boolean,
    val acceptsExtendedArea: Boolean,
    val rating: Double,
    val totalRides: Int,
    val acceptanceRate: Double,
    val cancellationRate: Double,
    val completionRate: Double
)

/**
 * Emergency contact data model.
 * Requirements: 9.7
 */
data class EmergencyContact(
    val id: String,
    val name: String,
    val phoneNumber: String,
    val relationship: String?
) {
    init {
        require(name.isNotBlank()) { "Name cannot be blank" }
        require(phoneNumber.isNotBlank()) { "Phone number cannot be blank" }
    }
}

/**
 * Vehicle details for a driver.
 * Requirements: 2.5
 */
data class VehicleDetails(
    val make: String,
    val model: String,
    val year: Int,
    val color: String,
    val licensePlate: String,
    val vehicleType: VehicleType
)

/**
 * Vehicle type enum.
 */
enum class VehicleType {
    SEDAN,
    SUV,
    HATCHBACK,
    AUTO
}

/**
 * Availability request for driver.
 * Requirements: 11.1, 11.2
 */
data class AvailabilityRequest(
    val isAvailable: Boolean,
    val location: Location?
)

/**
 * Ride request notification for driver.
 * Requirements: 12.1, 12.2
 */
data class RideRequestNotification(
    val ride: Ride,
    val expiresAt: LocalDateTime,
    val estimatedDistance: Double?,
    val estimatedDuration: Int?
)

/**
 * Earnings data for driver.
 * Requirements: 14.1, 14.2, 14.3, 14.4
 */
data class EarningsData(
    val totalEarnings: Double,
    val todayEarnings: Double,
    val weekEarnings: Double,
    val monthEarnings: Double,
    val totalRides: Int,
    val averageFare: Double,
    val pendingEarnings: Double,
    val rides: List<EarningsRide>
)

/**
 * Earnings ride entry.
 */
data class EarningsRide(
    val rideId: String,
    val date: LocalDateTime,
    val fare: Double,
    val distance: Double?,
    val duration: Int?,
    val pickupAddress: String?,
    val dropoffAddress: String?
)

/**
 * Driver performance metrics.
 * Requirements: 16.1, 16.2, 16.3
 */
data class DriverPerformance(
    val averageRating: Double,
    val totalRatings: Int,
    val ratingBreakdown: Map<Int, Int>, // Star count to number of ratings
    val acceptanceRate: Double,
    val cancellationRate: Double,
    val completionRate: Double,
    val totalRides: Int,
    val improvementSuggestions: List<String>
)
