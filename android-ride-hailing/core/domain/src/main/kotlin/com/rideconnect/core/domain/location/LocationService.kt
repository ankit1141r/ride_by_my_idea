package com.rideconnect.core.domain.location

import com.rideconnect.core.domain.model.Location
import kotlinx.coroutines.flow.Flow

interface LocationService {
    /**
     * Start receiving location updates at the specified interval
     * @param intervalMs Update interval in milliseconds (default: 10000ms = 10 seconds)
     */
    fun startLocationUpdates(intervalMs: Long = 10000L)
    
    /**
     * Stop receiving location updates
     */
    fun stopLocationUpdates()
    
    /**
     * Flow of location updates
     */
    val locationFlow: Flow<Location>
    
    /**
     * Get the current location once
     * @return Current location or null if unavailable
     */
    suspend fun getCurrentLocation(): Location?
    
    /**
     * Check if location services are enabled
     */
    fun isLocationEnabled(): Boolean
    
    /**
     * Check if location permissions are granted
     */
    fun hasLocationPermission(): Boolean
}
