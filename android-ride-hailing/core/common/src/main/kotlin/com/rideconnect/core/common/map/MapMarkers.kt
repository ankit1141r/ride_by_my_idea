package com.rideconnect.core.common.map

import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember
import androidx.compose.ui.graphics.Color
import com.google.android.gms.maps.model.BitmapDescriptorFactory
import com.google.android.gms.maps.model.LatLng
import com.google.maps.android.compose.Marker
import com.google.maps.android.compose.MarkerState
import com.google.maps.android.compose.Polyline
import com.rideconnect.core.domain.model.Location

/**
 * Composable for displaying a pickup location marker.
 * 
 * Requirements: 18.2
 */
@Composable
fun PickupMarker(
    location: Location,
    title: String = "Pickup Location",
    onClick: () -> Unit = {}
) {
    val markerState = remember(location) {
        MarkerState(position = location.toLatLng())
    }
    
    Marker(
        state = markerState,
        title = title,
        icon = BitmapDescriptorFactory.defaultMarker(BitmapDescriptorFactory.HUE_GREEN),
        onClick = {
            onClick()
            true
        }
    )
}

/**
 * Composable for displaying a dropoff location marker.
 * 
 * Requirements: 18.2
 */
@Composable
fun DropoffMarker(
    location: Location,
    title: String = "Dropoff Location",
    onClick: () -> Unit = {}
) {
    val markerState = remember(location) {
        MarkerState(position = location.toLatLng())
    }
    
    Marker(
        state = markerState,
        title = title,
        icon = BitmapDescriptorFactory.defaultMarker(BitmapDescriptorFactory.HUE_RED),
        onClick = {
            onClick()
            true
        }
    )
}

/**
 * Composable for displaying a driver location marker.
 * 
 * Requirements: 18.2, 6.1
 */
@Composable
fun DriverMarker(
    location: Location,
    driverName: String = "Driver",
    rotation: Float = 0f,
    onClick: () -> Unit = {}
) {
    val markerState = remember(location) {
        MarkerState(position = location.toLatLng())
    }
    
    // Update marker position when location changes
    LaunchedEffect(location) {
        markerState.position = location.toLatLng()
    }
    
    Marker(
        state = markerState,
        title = driverName,
        rotation = rotation,
        icon = BitmapDescriptorFactory.defaultMarker(BitmapDescriptorFactory.HUE_BLUE),
        onClick = {
            onClick()
            true
        }
    )
}

/**
 * Composable for displaying a route polyline.
 * 
 * Requirements: 18.5, 18.6
 */
@Composable
fun RoutePolyline(
    points: List<LatLng>,
    color: Color = Color.Blue,
    width: Float = 10f,
    onClick: () -> Unit = {}
) {
    if (points.isNotEmpty()) {
        Polyline(
            points = points,
            color = color,
            width = width,
            onClick = {
                onClick()
            }
        )
    }
}

/**
 * Decode polyline string to list of LatLng points.
 * Uses Google's polyline encoding algorithm.
 * 
 * Requirements: 18.5
 */
fun decodePolyline(encoded: String): List<LatLng> {
    val poly = ArrayList<LatLng>()
    var index = 0
    val len = encoded.length
    var lat = 0
    var lng = 0

    while (index < len) {
        var b: Int
        var shift = 0
        var result = 0
        do {
            b = encoded[index++].code - 63
            result = result or (b and 0x1f shl shift)
            shift += 5
        } while (b >= 0x20)
        val dlat = if (result and 1 != 0) (result shr 1).inv() else result shr 1
        lat += dlat

        shift = 0
        result = 0
        do {
            b = encoded[index++].code - 63
            result = result or (b and 0x1f shl shift)
            shift += 5
        } while (b >= 0x20)
        val dlng = if (result and 1 != 0) (result shr 1).inv() else result shr 1
        lng += dlng

        val latLng = LatLng(
            lat.toDouble() / 1E5,
            lng.toDouble() / 1E5
        )
        poly.add(latLng)
    }

    return poly
}
