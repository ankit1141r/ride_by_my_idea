package com.rideconnect.core.network.api

import com.rideconnect.core.network.dto.AvailabilityRequestDto
import com.rideconnect.core.network.dto.DriverPerformanceDto
import com.rideconnect.core.network.dto.EarningsResponseDto
import com.rideconnect.core.network.dto.RideResponseDto
import retrofit2.Response
import retrofit2.http.*

/**
 * API interface for driver-specific operations.
 * Requirements: 11.1, 11.2, 12.1, 14.1, 14.2, 16.1
 */
interface DriverApi {
    
    /**
     * Set driver availability status.
     * Requirements: 11.1, 11.2
     */
    @POST("/api/drivers/availability")
    suspend fun setAvailability(
        @Body request: AvailabilityRequestDto
    ): Response<Unit>
    
    /**
     * Accept a ride request.
     * Requirements: 12.4
     */
    @POST("/api/rides/{rideId}/accept")
    suspend fun acceptRide(
        @Path("rideId") rideId: String
    ): Response<RideResponseDto>
    
    /**
     * Reject a ride request.
     * Requirements: 12.5
     */
    @POST("/api/rides/{rideId}/reject")
    suspend fun rejectRide(
        @Path("rideId") rideId: String,
        @Body reason: Map<String, String>
    ): Response<Unit>
    
    /**
     * Start a ride.
     * Requirements: 13.3
     */
    @POST("/api/rides/{rideId}/start")
    suspend fun startRide(
        @Path("rideId") rideId: String
    ): Response<Unit>
    
    /**
     * Complete a ride.
     * Requirements: 13.6
     */
    @POST("/api/rides/{rideId}/complete")
    suspend fun completeRide(
        @Path("rideId") rideId: String
    ): Response<Unit>
    
    /**
     * Cancel a ride.
     * Requirements: 13.8
     */
    @POST("/api/rides/{rideId}/cancel")
    suspend fun cancelRide(
        @Path("rideId") rideId: String,
        @Body reason: Map<String, String>
    ): Response<Unit>
    
    /**
     * Get driver earnings.
     * Requirements: 14.1, 14.2
     */
    @GET("/api/drivers/earnings")
    suspend fun getEarnings(
        @Query("start_date") startDate: String,
        @Query("end_date") endDate: String
    ): Response<EarningsResponseDto>
    
    /**
     * Get driver performance metrics.
     * Requirements: 16.1, 16.2, 16.3
     */
    @GET("/api/drivers/performance")
    suspend fun getPerformance(): Response<DriverPerformanceDto>
    
    /**
     * Update driver location.
     * Requirements: 11.3
     */
    @POST("/api/drivers/location")
    suspend fun updateLocation(
        @Body location: Map<String, Double>
    ): Response<Unit>
    
    /**
     * Register device token for push notifications.
     * Requirements: 19.1, 19.2
     */
    @POST("/api/drivers/device-token")
    suspend fun registerDeviceToken(
        @Body token: String
    ): Response<Unit>
}
