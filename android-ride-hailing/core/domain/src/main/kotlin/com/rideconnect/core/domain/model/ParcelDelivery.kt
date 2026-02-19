package com.rideconnect.core.domain.model

/**
 * Parcel delivery domain models.
 * 
 * Requirements: 5.1, 5.2, 5.3
 */
data class ParcelDelivery(
    val id: String,
    val senderId: String,
    val driverId: String?,
    val pickupLocation: Location,
    val dropoffLocation: Location,
    val parcelSize: ParcelSize,
    val senderName: String,
    val senderPhone: String,
    val recipientName: String,
    val recipientPhone: String,
    val instructions: String?,
    val status: ParcelStatus,
    val fare: Double?,
    val distance: Double?,
    val requestedAt: Long,
    val pickedUpAt: Long? = null,
    val deliveredAt: Long? = null
)

/**
 * Parcel size categories.
 * Requirements: 5.1
 */
enum class ParcelSize {
    SMALL,   // Up to 5kg
    MEDIUM,  // 5-15kg
    LARGE    // 15-30kg
}

/**
 * Parcel delivery status.
 * Requirements: 5.6, 5.7
 */
enum class ParcelStatus {
    REQUESTED,      // Parcel delivery requested
    ACCEPTED,       // Driver accepted the delivery
    PICKED_UP,      // Driver picked up the parcel
    IN_TRANSIT,     // Parcel is being delivered
    DELIVERED,      // Parcel delivered successfully
    CANCELLED       // Delivery was cancelled
}

/**
 * Request to create a parcel delivery.
 * Requirements: 5.1, 5.2, 5.3
 */
data class ParcelDeliveryRequest(
    val pickupLocation: Location,
    val dropoffLocation: Location,
    val parcelSize: ParcelSize,
    val senderName: String,
    val senderPhone: String,
    val recipientName: String,
    val recipientPhone: String,
    val instructions: String?
)

/**
 * Response from parcel delivery API.
 */
data class ParcelDeliveryResponse(
    val id: String,
    val senderId: String,
    val driverId: String?,
    val pickupLocation: Location,
    val dropoffLocation: Location,
    val parcelSize: String,
    val senderName: String,
    val senderPhone: String,
    val recipientName: String,
    val recipientPhone: String,
    val instructions: String?,
    val status: String,
    val fare: Double?,
    val distance: Double?,
    val requestedAt: Long,
    val pickedUpAt: Long?,
    val deliveredAt: Long?
)
