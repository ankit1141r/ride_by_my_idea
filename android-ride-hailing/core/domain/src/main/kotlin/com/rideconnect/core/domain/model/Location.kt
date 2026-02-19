package com.rideconnect.core.domain.model

data class Location(
    val latitude: Double,
    val longitude: Double,
    val address: String? = null,
    val placeId: String? = null,
    val accuracy: Float? = null,
    val timestamp: Long = System.currentTimeMillis()
)
