package com.rideconnect.core.network.api

import com.rideconnect.core.network.dto.CancelScheduledRideRequestDto
import com.rideconnect.core.network.dto.ScheduledRideRequestDto
import com.rideconnect.core.network.dto.ScheduledRideResponseDto
import retrofit2.Response
import retrofit2.http.*

/**
 * API interface for scheduled ride operations.
 * 
 * Requirements: 4.1, 4.4
 */
interface ScheduledRideApi {
    
    @POST("/api/rides/schedule")
    suspend fun scheduleRide(
        @Body request: ScheduledRideRequestDto
    ): Response<ScheduledRideResponseDto>
    
    @GET("/api/rides/scheduled")
    suspend fun getScheduledRides(
        @Query("page") page: Int = 0,
        @Query("page_size") pageSize: Int = 20
    ): Response<List<ScheduledRideResponseDto>>
    
    @GET("/api/rides/scheduled/{rideId}")
    suspend fun getScheduledRideDetails(
        @Path("rideId") rideId: String
    ): Response<ScheduledRideResponseDto>
    
    @POST("/api/rides/scheduled/{rideId}/cancel")
    suspend fun cancelScheduledRide(
        @Path("rideId") rideId: String,
        @Body request: CancelScheduledRideRequestDto
    ): Response<Unit>
}
