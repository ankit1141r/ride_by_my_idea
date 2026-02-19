package com.rideconnect.core.network.dto

import com.google.gson.annotations.SerializedName

/**
 * DTO for availability request.
 * Requirements: 11.1, 11.2
 */
data class AvailabilityRequestDto(
    @SerializedName("is_available")
    val isAvailable: Boolean,
    
    @SerializedName("latitude")
    val latitude: Double?,
    
    @SerializedName("longitude")
    val longitude: Double?
)

/**
 * DTO for earnings response.
 * Requirements: 14.1, 14.2, 14.3, 14.4
 */
data class EarningsResponseDto(
    @SerializedName("total_earnings")
    val totalEarnings: Double,
    
    @SerializedName("today_earnings")
    val todayEarnings: Double,
    
    @SerializedName("week_earnings")
    val weekEarnings: Double,
    
    @SerializedName("month_earnings")
    val monthEarnings: Double,
    
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
 * DTO for earnings ride entry.
 */
data class EarningsRideDto(
    @SerializedName("ride_id")
    val rideId: String,
    
    @SerializedName("date")
    val date: String,
    
    @SerializedName("fare")
    val fare: Double,
    
    @SerializedName("distance")
    val distance: Double?,
    
    @SerializedName("duration")
    val duration: Int?,
    
    @SerializedName("pickup_address")
    val pickupAddress: String?,
    
    @SerializedName("dropoff_address")
    val dropoffAddress: String?
)

/**
 * DTO for driver performance metrics.
 * Requirements: 16.1, 16.2, 16.3
 */
data class DriverPerformanceDto(
    @SerializedName("average_rating")
    val averageRating: Double,
    
    @SerializedName("total_ratings")
    val totalRatings: Int,
    
    @SerializedName("rating_breakdown")
    val ratingBreakdown: Map<String, Int>,
    
    @SerializedName("acceptance_rate")
    val acceptanceRate: Double,
    
    @SerializedName("cancellation_rate")
    val cancellationRate: Double,
    
    @SerializedName("completion_rate")
    val completionRate: Double,
    
    @SerializedName("total_rides")
    val totalRides: Int,
    
    @SerializedName("improvement_suggestions")
    val improvementSuggestions: List<String>
)

/**
 * DTO for driver details.
 */
data class DriverDto(
    @SerializedName("id")
    val id: String,
    
    @SerializedName("user_id")
    val userId: String,
    
    @SerializedName("vehicle_make")
    val vehicleMake: String,
    
    @SerializedName("vehicle_model")
    val vehicleModel: String,
    
    @SerializedName("vehicle_year")
    val vehicleYear: Int,
    
    @SerializedName("vehicle_color")
    val vehicleColor: String,
    
    @SerializedName("license_plate")
    val licensePlate: String,
    
    @SerializedName("vehicle_type")
    val vehicleType: String,
    
    @SerializedName("license_number")
    val licenseNumber: String,
    
    @SerializedName("is_available")
    val isAvailable: Boolean,
    
    @SerializedName("accepts_parcel_delivery")
    val acceptsParcelDelivery: Boolean,
    
    @SerializedName("accepts_extended_area")
    val acceptsExtendedArea: Boolean,
    
    @SerializedName("rating")
    val rating: Double,
    
    @SerializedName("total_rides")
    val totalRides: Int,
    
    @SerializedName("acceptance_rate")
    val acceptanceRate: Double,
    
    @SerializedName("cancellation_rate")
    val cancellationRate: Double,
    
    @SerializedName("completion_rate")
    val completionRate: Double
)

/**
 * DTO for ride request notification.
 * Requirements: 12.1, 12.2
 */
data class RideRequestNotificationDto(
    @SerializedName("ride")
    val ride: RideResponseDto,
    
    @SerializedName("expires_at")
    val expiresAt: String,
    
    @SerializedName("estimated_distance")
    val estimatedDistance: Double?,
    
    @SerializedName("estimated_duration")
    val estimatedDuration: Int?
)
