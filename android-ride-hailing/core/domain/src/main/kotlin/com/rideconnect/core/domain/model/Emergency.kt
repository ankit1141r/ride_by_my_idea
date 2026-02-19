package com.rideconnect.core.domain.model

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
 * SOS request data model.
 * Requirements: 9.1, 9.2
 */
data class SOSRequest(
    val rideId: String,
    val location: Location,
    val timestamp: Long = System.currentTimeMillis()
)

/**
 * SOS alert response from backend.
 * Requirements: 9.1, 9.6
 */
data class SOSAlert(
    val id: String,
    val rideId: String,
    val userId: String,
    val location: Location,
    val timestamp: Long,
    val status: SOSStatus
)

/**
 * SOS alert status.
 */
enum class SOSStatus {
    ACTIVE,
    RESOLVED,
    CANCELLED
}

/**
 * Request to add an emergency contact.
 * Requirements: 9.7
 */
data class AddEmergencyContactRequest(
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
 * Request to share ride with emergency contacts.
 * Requirements: 9.4
 */
data class ShareRideRequest(
    val rideId: String,
    val contactIds: List<String>
) {
    init {
        require(contactIds.isNotEmpty()) { "At least one contact must be selected" }
    }
}

/**
 * Ride sharing link response.
 * Requirements: 9.4
 */
data class RideShareLink(
    val rideId: String,
    val shareUrl: String,
    val expiresAt: Long
)
