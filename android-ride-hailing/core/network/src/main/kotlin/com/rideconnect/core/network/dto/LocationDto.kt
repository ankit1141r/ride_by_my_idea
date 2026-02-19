package com.rideconnect.core.network.dto

import com.google.gson.annotations.SerializedName

/**
 * DTO for location update requests.
 * 
 * Requirements: 11.3
 */
data class LocationUpdateRequest(
    @SerializedName("latitude")
    val latitude: Double,
    
    @SerializedName("longitude")
    val longitude: Double,
    
    @SerializedName("accuracy")
    val accuracy: Float,
    
    @SerializedName("timestamp")
    val timestamp: Long
)
