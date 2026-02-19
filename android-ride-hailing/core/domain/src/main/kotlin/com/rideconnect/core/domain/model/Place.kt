package com.rideconnect.core.domain.model

/**
 * Represents a place from Google Places API.
 * 
 * Requirements: 18.3, 18.4
 */
data class Place(
    val placeId: String,
    val name: String,
    val address: String,
    val location: Location,
    val types: List<String> = emptyList()
)
