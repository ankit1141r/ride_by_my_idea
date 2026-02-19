package com.rideconnect.core.domain.location

import com.rideconnect.core.common.result.Result
import com.rideconnect.core.domain.model.Location
import com.rideconnect.core.domain.model.Place
import com.rideconnect.core.domain.model.Route

/**
 * Repository interface for location-related operations.
 * 
 * Requirements: 18.3, 18.4
 */
interface LocationRepository {
    /**
     * Update driver location on the backend.
     * Called every 10 seconds while driver is online.
     */
    suspend fun updateLocation(location: Location): Result<Unit>
    
    /**
     * Search for places using Google Places API.
     * Returns autocomplete suggestions based on query.
     */
    suspend fun searchPlaces(query: String, location: Location? = null): Result<List<Place>>
    
    /**
     * Get detailed information about a specific place.
     */
    suspend fun getPlaceDetails(placeId: String): Result<Place>
    
    /**
     * Calculate route between two locations.
     * Returns route with polyline, distance, and estimated time.
     */
    suspend fun calculateRoute(origin: Location, destination: Location): Result<Route>
}
