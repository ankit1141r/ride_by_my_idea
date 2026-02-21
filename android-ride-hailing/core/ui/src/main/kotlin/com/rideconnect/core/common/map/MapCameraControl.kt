package com.rideconnect.core.common.map

import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import com.google.android.gms.maps.CameraUpdateFactory
import com.google.android.gms.maps.model.LatLng
import com.google.android.gms.maps.model.LatLngBounds
import com.google.maps.android.compose.CameraPositionState
import com.rideconnect.core.domain.model.Location
import kotlinx.coroutines.delay

/**
 * Camera control utilities for Google Maps.
 * 
 * Requirements: 6.8, 18.7
 */

/**
 * Animate camera to show all markers within bounds.
 * 
 * Requirements: 18.7
 */
@Composable
fun AnimateCameraToBounds(
    cameraPositionState: CameraPositionState,
    locations: List<Location>,
    padding: Int = 100
) {
    LaunchedEffect(locations) {
        if (locations.size >= 2) {
            val bounds = calculateBounds(locations)
            cameraPositionState.animate(
                CameraUpdateFactory.newLatLngBounds(bounds, padding),
                durationMs = 1000
            )
        } else if (locations.size == 1) {
            cameraPositionState.animate(
                CameraUpdateFactory.newLatLngZoom(locations[0].toLatLng(), 15f),
                durationMs = 1000
            )
        }
    }
}

/**
 * Smoothly animate camera to a location.
 * 
 * Requirements: 6.8
 */
@Composable
fun AnimateCameraToLocation(
    cameraPositionState: CameraPositionState,
    location: Location,
    zoom: Float = 15f,
    animate: Boolean = true
) {
    LaunchedEffect(location) {
        if (animate) {
            cameraPositionState.animate(
                CameraUpdateFactory.newLatLngZoom(location.toLatLng(), zoom),
                durationMs = 1000
            )
        } else {
            cameraPositionState.move(
                CameraUpdateFactory.newLatLngZoom(location.toLatLng(), zoom)
            )
        }
    }
}

/**
 * Animate camera to follow driver location with smooth updates.
 * 
 * Requirements: 6.3
 */
@Composable
fun FollowDriverLocation(
    cameraPositionState: CameraPositionState,
    driverLocation: Location?,
    isFollowing: Boolean = true,
    zoom: Float = 16f
) {
    LaunchedEffect(driverLocation, isFollowing) {
        if (driverLocation != null && isFollowing) {
            // Smooth animation with delay to avoid jittery updates
            delay(500)
            cameraPositionState.animate(
                CameraUpdateFactory.newLatLngZoom(driverLocation.toLatLng(), zoom),
                durationMs = 800
            )
        }
    }
}

/**
 * Calculate bounds that include all locations.
 * 
 * Requirements: 18.7
 */
fun calculateBounds(locations: List<Location>): LatLngBounds {
    val builder = LatLngBounds.Builder()
    locations.forEach { location ->
        builder.include(location.toLatLng())
    }
    return builder.build()
}

/**
 * Calculate bounds from LatLng list.
 */
fun calculateBoundsFromLatLng(points: List<LatLng>): LatLngBounds {
    val builder = LatLngBounds.Builder()
    points.forEach { point ->
        builder.include(point)
    }
    return builder.build()
}

/**
 * Check if location is within visible map bounds.
 */
fun isLocationInBounds(location: Location, bounds: LatLngBounds): Boolean {
    return bounds.contains(location.toLatLng())
}

/**
 * Calculate center point of multiple locations.
 */
fun calculateCenter(locations: List<Location>): Location {
    if (locations.isEmpty()) {
        return Location(0.0, 0.0, null, null, null, 0L)
    }
    
    var totalLat = 0.0
    var totalLng = 0.0
    
    locations.forEach { location ->
        totalLat += location.latitude
        totalLng += location.longitude
    }
    
    return Location(
        latitude = totalLat / locations.size,
        longitude = totalLng / locations.size,
        accuracy = null,
        timestamp = System.currentTimeMillis()
    )
}

/**
 * Adjust camera to show all points within bounds.
 * Requirements: 6.8, 18.7
 */
suspend fun adjustCameraBounds(
    cameraPositionState: CameraPositionState,
    points: List<LatLng>,
    padding: Int = 100
) {
    if (points.size >= 2) {
        val bounds = calculateBoundsFromLatLng(points)
        cameraPositionState.animate(
            CameraUpdateFactory.newLatLngBounds(bounds, padding),
            durationMs = 1000
        )
    } else if (points.size == 1) {
        cameraPositionState.animate(
            CameraUpdateFactory.newLatLngZoom(points[0], 15f),
            durationMs = 1000
        )
    }
}
