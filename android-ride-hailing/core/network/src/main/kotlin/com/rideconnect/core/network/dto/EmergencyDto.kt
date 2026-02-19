package com.rideconnect.core.network.dto

import com.google.gson.annotations.SerializedName

data class SOSRequestDto(
    @SerializedName("ride_id")
    val rideId: String,
    @SerializedName("latitude")
    val latitude: Double,
    @SerializedName("longitude")
    val longitude: Double,
    @SerializedName("timestamp")
    val timestamp: Long
)

data class EmergencyContactRequestDto(
    @SerializedName("name")
    val name: String,
    @SerializedName("phone_number")
    val phoneNumber: String,
    @SerializedName("relationship")
    val relationship: String?
)

data class EmergencyContactResponseDto(
    @SerializedName("id")
    val id: String,
    @SerializedName("user_id")
    val userId: String,
    @SerializedName("name")
    val name: String,
    @SerializedName("phone_number")
    val phoneNumber: String,
    @SerializedName("relationship")
    val relationship: String?
)

data class ShareRideRequestDto(
    @SerializedName("ride_id")
    val rideId: String,
    @SerializedName("contact_ids")
    val contactIds: List<String>
)

data class ShareRideResponseDto(
    @SerializedName("tracking_link")
    val trackingLink: String
)
