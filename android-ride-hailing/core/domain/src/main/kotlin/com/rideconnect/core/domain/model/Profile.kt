package com.rideconnect.core.domain.model

data class ProfileUpdateRequest(
    val name: String? = null,
    val email: String? = null,
    val profilePhotoUrl: String? = null
)

data class VehicleDetails(
    val make: String,
    val model: String,
    val year: Int,
    val color: String,
    val licensePlate: String,
    val vehicleType: VehicleType
)

enum class VehicleType {
    SEDAN,
    SUV,
    HATCHBACK,
    AUTO
}

data class EmergencyContact(
    val id: String,
    val name: String,
    val phoneNumber: String,
    val relationship: String? = null
)

data class Driver(
    val user: User,
    val vehicleDetails: VehicleDetails?,
    val licenseNumber: String?,
    val isAvailable: Boolean = false,
    val currentLocation: Location? = null,
    val acceptsParcelDelivery: Boolean = false,
    val acceptsExtendedArea: Boolean = false
)
