package com.rideconnect.core.network.dto

import com.google.gson.annotations.SerializedName

data class ParcelDeliveryRequestDto(
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
    @SerializedName("parcel_size")
    val parcelSize: String,
    @SerializedName("sender_name")
    val senderName: String,
    @SerializedName("sender_phone")
    val senderPhone: String,
    @SerializedName("recipient_name")
    val recipientName: String,
    @SerializedName("recipient_phone")
    val recipientPhone: String,
    @SerializedName("instructions")
    val instructions: String?
)

data class ParcelDeliveryResponseDto(
    @SerializedName("id")
    val id: String,
    @SerializedName("sender_id")
    val senderId: String,
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
    @SerializedName("parcel_size")
    val parcelSize: String,
    @SerializedName("sender_name")
    val senderName: String,
    @SerializedName("sender_phone")
    val senderPhone: String,
    @SerializedName("recipient_name")
    val recipientName: String,
    @SerializedName("recipient_phone")
    val recipientPhone: String,
    @SerializedName("instructions")
    val instructions: String?,
    @SerializedName("status")
    val status: String,
    @SerializedName("fare")
    val fare: Double?,
    @SerializedName("requested_at")
    val requestedAt: String,
    @SerializedName("picked_up_at")
    val pickedUpAt: String?,
    @SerializedName("delivered_at")
    val deliveredAt: String?
)
