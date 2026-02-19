package com.rideconnect.core.common.navigation

import android.content.Context
import android.content.Intent
import android.net.Uri
import com.rideconnect.core.domain.model.Location

/**
 * Helper class for integrating with Google Maps navigation
 */
object NavigationHelper {
    
    /**
     * Opens Google Maps with turn-by-turn navigation to the specified destination
     * 
     * @param context Android context
     * @param destination The destination location
     * @param origin Optional origin location (defaults to current location)
     * @param travelMode Travel mode: "d" for driving (default), "w" for walking, "b" for bicycling
     */
    fun startNavigation(
        context: Context,
        destination: Location,
        origin: Location? = null,
        travelMode: String = "d"
    ) {
        val uriBuilder = StringBuilder("google.navigation:q=")
        uriBuilder.append("${destination.latitude},${destination.longitude}")
        
        // Add origin if provided
        origin?.let {
            uriBuilder.append("&origin=${it.latitude},${it.longitude}")
        }
        
        // Add travel mode
        uriBuilder.append("&mode=$travelMode")
        
        val navigationUri = Uri.parse(uriBuilder.toString())
        val intent = Intent(Intent.ACTION_VIEW, navigationUri).apply {
            setPackage("com.google.android.apps.maps")
            flags = Intent.FLAG_ACTIVITY_NEW_TASK
        }
        
        try {
            context.startActivity(intent)
        } catch (e: Exception) {
            // Fallback to browser if Google Maps is not installed
            openInBrowser(context, destination, origin)
        }
    }
    
    /**
     * Opens Google Maps in the browser as a fallback
     */
    private fun openInBrowser(
        context: Context,
        destination: Location,
        origin: Location?
    ) {
        val uriBuilder = StringBuilder("https://www.google.com/maps/dir/?api=1")
        uriBuilder.append("&destination=${destination.latitude},${destination.longitude}")
        
        origin?.let {
            uriBuilder.append("&origin=${it.latitude},${it.longitude}")
        }
        
        val browserUri = Uri.parse(uriBuilder.toString())
        val intent = Intent(Intent.ACTION_VIEW, browserUri).apply {
            flags = Intent.FLAG_ACTIVITY_NEW_TASK
        }
        
        context.startActivity(intent)
    }
    
    /**
     * Checks if Google Maps is installed on the device
     */
    fun isGoogleMapsInstalled(context: Context): Boolean {
        return try {
            context.packageManager.getPackageInfo("com.google.android.apps.maps", 0)
            true
        } catch (e: Exception) {
            false
        }
    }
    
    /**
     * Opens Google Maps to show a location without navigation
     */
    fun showLocation(
        context: Context,
        location: Location,
        label: String? = null
    ) {
        val uriBuilder = StringBuilder("geo:${location.latitude},${location.longitude}")
        
        label?.let {
            uriBuilder.append("?q=${location.latitude},${location.longitude}($it)")
        }
        
        val locationUri = Uri.parse(uriBuilder.toString())
        val intent = Intent(Intent.ACTION_VIEW, locationUri).apply {
            setPackage("com.google.android.apps.maps")
            flags = Intent.FLAG_ACTIVITY_NEW_TASK
        }
        
        try {
            context.startActivity(intent)
        } catch (e: Exception) {
            // Fallback to browser
            val browserUri = Uri.parse(
                "https://www.google.com/maps/search/?api=1&query=${location.latitude},${location.longitude}"
            )
            val browserIntent = Intent(Intent.ACTION_VIEW, browserUri).apply {
                flags = Intent.FLAG_ACTIVITY_NEW_TASK
            }
            context.startActivity(browserIntent)
        }
    }
    
    /**
     * Opens Google Maps with directions between two points (without starting navigation)
     */
    fun showDirections(
        context: Context,
        origin: Location,
        destination: Location,
        travelMode: String = "d"
    ) {
        val uriBuilder = StringBuilder("https://www.google.com/maps/dir/?api=1")
        uriBuilder.append("&origin=${origin.latitude},${origin.longitude}")
        uriBuilder.append("&destination=${destination.latitude},${destination.longitude}")
        uriBuilder.append("&travelmode=$travelMode")
        
        val directionsUri = Uri.parse(uriBuilder.toString())
        val intent = Intent(Intent.ACTION_VIEW, directionsUri).apply {
            setPackage("com.google.android.apps.maps")
            flags = Intent.FLAG_ACTIVITY_NEW_TASK
        }
        
        try {
            context.startActivity(intent)
        } catch (e: Exception) {
            // Fallback to browser
            val browserIntent = Intent(Intent.ACTION_VIEW, directionsUri).apply {
                flags = Intent.FLAG_ACTIVITY_NEW_TASK
            }
            context.startActivity(browserIntent)
        }
    }
}

/**
 * Extension function to start navigation from a Location
 */
fun Location.navigateTo(context: Context, origin: Location? = null) {
    NavigationHelper.startNavigation(context, this, origin)
}

/**
 * Extension function to show a location on the map
 */
fun Location.showOnMap(context: Context, label: String? = null) {
    NavigationHelper.showLocation(context, this, label)
}
