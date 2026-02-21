package com.rideconnect.core.common.permission

import android.Manifest
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.*
import androidx.compose.ui.platform.LocalContext
import com.google.accompanist.permissions.ExperimentalPermissionsApi
import com.google.accompanist.permissions.isGranted
import com.google.accompanist.permissions.rememberMultiplePermissionsState
import com.google.accompanist.permissions.rememberPermissionState
import com.google.accompanist.permissions.shouldShowRationale

/**
 * Composable for requesting location permissions with rationale dialog.
 * 
 * Requirements: 29.1, 29.7
 */
@OptIn(ExperimentalPermissionsApi::class)
@Composable
fun RequestLocationPermission(
    onPermissionGranted: () -> Unit,
    onPermissionDenied: () -> Unit
) {
    val context = LocalContext.current
    var showRationale by remember { mutableStateOf(false) }
    
    val locationPermissionsState = rememberMultiplePermissionsState(
        permissions = listOf(
            Manifest.permission.ACCESS_FINE_LOCATION,
            Manifest.permission.ACCESS_COARSE_LOCATION
        )
    ) { permissions ->
        val allGranted = permissions.values.all { it }
        if (allGranted) {
            onPermissionGranted()
        } else {
            onPermissionDenied()
        }
    }
    
    LaunchedEffect(Unit) {
        when {
            locationPermissionsState.allPermissionsGranted -> {
                onPermissionGranted()
            }
            locationPermissionsState.shouldShowRationale -> {
                showRationale = true
            }
            else -> {
                locationPermissionsState.launchMultiplePermissionRequest()
            }
        }
    }
    
    if (showRationale) {
        LocationPermissionRationaleDialog(
            onConfirm = {
                showRationale = false
                locationPermissionsState.launchMultiplePermissionRequest()
            },
            onDismiss = {
                showRationale = false
                onPermissionDenied()
            }
        )
    }
}

/**
 * Composable for requesting background location permission (Android 10+).
 * Should be called after foreground location permission is granted.
 * 
 * Requirements: 29.5
 */
@OptIn(ExperimentalPermissionsApi::class)
@Composable
fun RequestBackgroundLocationPermission(
    onPermissionGranted: () -> Unit,
    onPermissionDenied: () -> Unit
) {
    var showRationale by remember { mutableStateOf(false) }
    
    val backgroundLocationPermissionState = rememberPermissionState(
        permission = Manifest.permission.ACCESS_BACKGROUND_LOCATION
    ) { isGranted ->
        if (isGranted) {
            onPermissionGranted()
        } else {
            onPermissionDenied()
        }
    }
    
    LaunchedEffect(Unit) {
        when {
            backgroundLocationPermissionState.status.isGranted -> {
                onPermissionGranted()
            }
            backgroundLocationPermissionState.status.shouldShowRationale -> {
                showRationale = true
            }
            else -> {
                backgroundLocationPermissionState.launchPermissionRequest()
            }
        }
    }
    
    if (showRationale) {
        BackgroundLocationPermissionRationaleDialog(
            onConfirm = {
                showRationale = false
                backgroundLocationPermissionState.launchPermissionRequest()
            },
            onDismiss = {
                showRationale = false
                onPermissionDenied()
            }
        )
    }
}

@Composable
private fun LocationPermissionRationaleDialog(
    onConfirm: () -> Unit,
    onDismiss: () -> Unit
) {
    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text("Location Permission Required") },
        text = {
            Text(
                "This app needs access to your location to show your current position " +
                        "on the map and match you with nearby rides. Your location is only " +
                        "used while you're using the app."
            )
        },
        confirmButton = {
            TextButton(onClick = onConfirm) {
                Text("Grant Permission")
            }
        },
        dismissButton = {
            TextButton(onClick = onDismiss) {
                Text("Cancel")
            }
        }
    )
}

@Composable
private fun BackgroundLocationPermissionRationaleDialog(
    onConfirm: () -> Unit,
    onDismiss: () -> Unit
) {
    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text("Background Location Permission") },
        text = {
            Text(
                "To receive ride requests while the app is in the background, " +
                        "we need permission to access your location all the time. " +
                        "This allows us to match you with nearby riders even when " +
                        "you're not actively using the app."
            )
        },
        confirmButton = {
            TextButton(onClick = onConfirm) {
                Text("Grant Permission")
            }
        },
        dismissButton = {
            TextButton(onClick = onDismiss) {
                Text("Not Now")
            }
        }
    )
}
