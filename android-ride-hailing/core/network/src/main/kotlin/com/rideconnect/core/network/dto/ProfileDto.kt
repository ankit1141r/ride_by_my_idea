package com.rideconnect.core.network.dto

import com.google.gson.annotations.SerializedName

data class ProfileUpdateRequestDto(
    @SerializedName("name")
    val name: String? = null,
    @SerializedName("email")
    val email: String? = null,
    @SerializedName("profile_photo_url")
    val profilePhotoUrl: String? = null
)

data class VehicleDetailsDto(
    @SerializedName("make")
    val make: String,
    @SerializedName("model")
    val model: String,
    @SerializedName("year")
    val year: Int,
    @SerializedName("color")
    val color: String,
    @SerializedName("license_plate")
    val licensePlate: String,
    @SerializedName("vehicle_type")
    val vehicleType: String
)

data class VehicleUpdateRequestDto(
    @SerializedName("make")
    val make: String,
    @SerializedName("model")
    val model: String,
    @SerializedName("year")
    val year: Int,
    @SerializedName("color")
    val color: String,
    @SerializedName("license_plate")
    val licensePlate: String,
    @SerializedName("vehicle_type")
    val vehicleType: String,
    @SerializedName("license_number")
    val licenseNumber: String
)

data class EmergencyContactDto(
    @SerializedName("id")
    val id: String,
    @SerializedName("name")
    val name: String,
    @SerializedName("phone_number")
    val phoneNumber: String,
    @SerializedName("relationship")
    val relationship: String?
)

data class EmergencyContactRequestDto(
    @SerializedName("name")
    val name: String,
    @SerializedName("phone_number")
    val phoneNumber: String,
    @SerializedName("relationship")
    val relationship: String? = null
)

data class ProfilePhotoUploadResponse(
    @SerializedName("photo_url")
    val photoUrl: String
)
