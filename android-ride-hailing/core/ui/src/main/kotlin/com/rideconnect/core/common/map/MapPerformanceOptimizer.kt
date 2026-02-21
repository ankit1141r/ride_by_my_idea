package com.rideconnect.core.common.map

import com.google.android.gms.maps.GoogleMap
import com.google.android.gms.maps.model.LatLng
import com.google.android.gms.maps.model.Marker
import com.google.android.gms.maps.model.MarkerOptions
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import kotlin.math.abs

/**
 * Utility for optimizing Google Maps performance
 * Requirements: 23.4
 */
class MapPerformanceOptimizer {
    
    private var markerUpdateJob: Job? = null
    private val markerCache = mutableMapOf<String, Marker>()
    private var lastUpdateTime = 0L
    
    companion object {
        // Minimum time between marker updates (milliseconds)
        private const val MIN_UPDATE_INTERVAL_MS = 1000L
        
        // Minimum distance to trigger marker update (meters)
        private const val MIN_UPDATE_DISTANCE_METERS = 10.0
        
        // Maximum number of markers to display
        private const val MAX_MARKERS = 50
    }
    
    /**
     * Update marker position with throttling to reduce rendering overhead
     * Requirements: 23.4
     */
    fun updateMarkerThrottled(
        scope: CoroutineScope,
        markerId: String,
        newPosition: LatLng,
        updateMarker: (LatLng) -> Unit
    ) {
        val currentTime = System.currentTimeMillis()
        val timeSinceLastUpdate = currentTime - lastUpdateTime
        
        // Cancel pending update if exists
        markerUpdateJob?.cancel()
        
        // Check if enough time has passed
        if (timeSinceLastUpdate < MIN_UPDATE_INTERVAL_MS) {
            // Schedule delayed update
            markerUpdateJob = scope.launch(Dispatchers.Main) {
                delay(MIN_UPDATE_INTERVAL_MS - timeSinceLastUpdate)
                updateMarker(newPosition)
                lastUpdateTime = System.currentTimeMillis()
            }
        } else {
            // Update immediately
            updateMarker(newPosition)
            lastUpdateTime = currentTime
        }
    }
    
    /**
     * Check if marker position change is significant enough to warrant update
     * Requirements: 23.4
     */
    fun shouldUpdateMarker(oldPosition: LatLng, newPosition: LatLng): Boolean {
        val distance = calculateDistance(oldPosition, newPosition)
        return distance >= MIN_UPDATE_DISTANCE_METERS
    }
    
    /**
     * Calculate distance between two LatLng points in meters (Haversine formula)
     */
    private fun calculateDistance(pos1: LatLng, pos2: LatLng): Double {
        val earthRadius = 6371000.0 // meters
        
        val lat1Rad = Math.toRadians(pos1.latitude)
        val lat2Rad = Math.toRadians(pos2.latitude)
        val deltaLat = Math.toRadians(pos2.latitude - pos1.latitude)
        val deltaLng = Math.toRadians(pos2.longitude - pos1.longitude)
        
        val a = Math.sin(deltaLat / 2) * Math.sin(deltaLat / 2) +
                Math.cos(lat1Rad) * Math.cos(lat2Rad) *
                Math.sin(deltaLng / 2) * Math.sin(deltaLng / 2)
        
        val c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))
        
        return earthRadius * c
    }
    
    /**
     * Manage marker cache to limit number of markers on map
     * Requirements: 23.4
     */
    fun addMarkerToCache(markerId: String, marker: Marker) {
        // Remove oldest marker if cache is full
        if (markerCache.size >= MAX_MARKERS) {
            val oldestEntry = markerCache.entries.first()
            oldestEntry.value.remove()
            markerCache.remove(oldestEntry.key)
        }
        
        markerCache[markerId] = marker
    }
    
    /**
     * Get marker from cache
     */
    fun getMarkerFromCache(markerId: String): Marker? {
        return markerCache[markerId]
    }
    
    /**
     * Remove marker from cache
     */
    fun removeMarkerFromCache(markerId: String) {
        markerCache[markerId]?.remove()
        markerCache.remove(markerId)
    }
    
    /**
     * Clear all markers from cache
     */
    fun clearMarkerCache() {
        markerCache.values.forEach { it.remove() }
        markerCache.clear()
    }
    
    /**
     * Configure map for optimal performance
     * Requirements: 23.4
     */
    fun configureMapForPerformance(googleMap: GoogleMap) {
        googleMap.apply {
            // Enable lite mode for better performance (if appropriate)
            // Note: Lite mode is set in XML, not programmatically
            
            // Disable unnecessary features
            uiSettings.isMapToolbarEnabled = false
            uiSettings.isIndoorLevelPickerEnabled = false
            
            // Enable map caching
            setMapType(GoogleMap.MAP_TYPE_NORMAL)
            
            // Limit zoom levels to reduce tile loading
            setMinZoomPreference(8f)
            setMaxZoomPreference(20f)
        }
    }
    
    /**
     * Batch marker updates to reduce rendering overhead
     */
    fun batchMarkerUpdates(
        googleMap: GoogleMap,
        markerUpdates: List<Pair<String, MarkerOptions>>,
        onComplete: () -> Unit
    ) {
        // Disable map gestures during batch update
        googleMap.uiSettings.setAllGesturesEnabled(false)
        
        // Add all markers
        markerUpdates.forEach { (markerId, options) ->
            val marker = googleMap.addMarker(options)
            marker?.let { addMarkerToCache(markerId, it) }
        }
        
        // Re-enable gestures
        googleMap.uiSettings.setAllGesturesEnabled(true)
        
        onComplete()
    }
    
    /**
     * Cancel any pending marker updates
     */
    fun cancelPendingUpdates() {
        markerUpdateJob?.cancel()
        markerUpdateJob = null
    }
}
