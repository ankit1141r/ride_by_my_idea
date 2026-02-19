package com.rideconnect.core.domain.model

/**
 * Represents a route between two locations.
 * 
 * Requirements: 18.5, 18.6
 */
data class Route(
    val polyline: String,
    val distanceMeters: Int,
    val durationSeconds: Int,
    val bounds: RouteBounds
)

data class RouteBounds(
    val northeast: Location,
    val southwest: Location
)
