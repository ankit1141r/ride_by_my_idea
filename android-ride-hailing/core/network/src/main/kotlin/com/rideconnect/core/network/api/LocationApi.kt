package com.rideconnect.core.network.api

import com.rideconnect.core.network.dto.LocationUpdateRequest
import retrofit2.http.Body
import retrofit2.http.POST

/**
 * API interface for location-related endpoints.
 * 
 * Requirements: 11.3
 */
interface LocationApi {
    
    @POST("location/driver")
    suspend fun updateDriverLocation(@Body request: LocationUpdateRequest)
}
