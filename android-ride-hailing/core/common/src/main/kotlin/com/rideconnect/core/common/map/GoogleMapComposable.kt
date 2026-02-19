package com.rideconnect.core.common.map

import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalLifecycleOwner
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.LifecycleEventObserver
import com.google.android.gms.maps.CameraUpdateFactory
import com.google.android.gms.maps.GoogleMap
import com.google.android.gms.maps.MapView
import com.google.android.gms.maps.model.CameraPosition
import com.google.android.gms.maps.model.LatLng
import com.google.maps.android.compose.*
import com.rideconnect.core.domain.model.Location

/**
 * Composable wrapper for Google Maps with lifecycle handling.
 * 
 * Requirements: 18.1, 18.2
 */
@Composable
fun RideConnectMap(
    modifier: Modifier = Modifier,
    cameraPositionState: CameraPositionState = rememberCameraPositionState(),
    uiSettings: MapUiSettings = remember { MapUiSettings() },
    properties: MapProperties = remember { MapProperties() },
    onMapLoaded: () -> Unit = {},
    onMapClick: (LatLng) -> Unit = {},
    content: @Composable () -> Unit = {}
) {
    GoogleMap(
        modifier = modifier.fillMaxSize(),
        cameraPositionState = cameraPositionState,
        uiSettings = uiSettings,
        properties = properties,
        onMapLoaded = onMapLoaded,
        onMapClick = onMapClick
    ) {
        content()
    }
}

/**
 * Remember camera position state with initial location.
 */
@Composable
fun rememberCameraPositionForLocation(
    location: Location?,
    zoom: Float = 15f
): CameraPositionState {
    return rememberCameraPositionState {
        position = if (location != null) {
            CameraPosition.fromLatLngZoom(
                LatLng(location.latitude, location.longitude),
                zoom
            )
        } else {
            // Default to Indore, India
            CameraPosition.fromLatLngZoom(
                LatLng(22.7196, 75.8577),
                12f
            )
        }
    }
}

/**
 * Extension function to convert Location to LatLng.
 */
fun Location.toLatLng(): LatLng {
    return LatLng(this.latitude, this.longitude)
}

/**
 * Extension function to convert LatLng to Location.
 */
fun LatLng.toLocation(): Location {
    return Location(
        latitude = this.latitude,
        longitude = this.longitude,
        accuracy = 0f,
        timestamp = System.currentTimeMillis()
    )
}

/**
 * Default map UI settings for RideConnect.
 */
@Composable
fun rememberRideConnectMapUiSettings(): MapUiSettings {
    return remember {
        MapUiSettings(
            zoomControlsEnabled = false,
            zoomGesturesEnabled = true,
            scrollGesturesEnabled = true,
            tiltGesturesEnabled = true,
            rotationGesturesEnabled = true,
            myLocationButtonEnabled = true,
            mapToolbarEnabled = false
        )
    }
}

/**
 * Default map properties for RideConnect.
 */
@Composable
fun rememberRideConnectMapProperties(
    isMyLocationEnabled: Boolean = false,
    showTraffic: Boolean = false
): MapProperties {
    return remember(isMyLocationEnabled, showTraffic) {
        MapProperties(
            isMyLocationEnabled = isMyLocationEnabled,
            isTrafficEnabled = showTraffic,
            mapType = com.google.android.gms.maps.model.MapType.NORMAL
        )
    }
}
