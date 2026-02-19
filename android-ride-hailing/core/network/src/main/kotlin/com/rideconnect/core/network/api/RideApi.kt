package com.rideconnect.core.network.api

import com.rideconnect.core.network.dto.CancelRideRequestDto
import com.rideconnect.core.network.dto.FareEstimateResponseDto
import com.rideconnect.core.network.dto.RejectRideRequestDto
import com.rideconnect.core.network.dto.RideRequestDto
import com.rideconnect.core.network.dto.RideResponseDto
import com.rideconnect.core.network.dto.ScheduledRideRequestDto
import com.rideconnect.core.network.dto.ScheduledRideResponseDto
import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.POST
import retrofit2.http.Path
import retrofit2.http.Query

interface RideApi {
    
    @POST("rides/request")
    suspend fun requestRide(@Body request: RideRequestDto): Response<RideResponseDto>
    
    @POST("rides/fare-estimate")
    suspend fun getFareEstimate(@Body request: RideRequestDto): Response<FareEstimateResponseDto>
    
    @POST("rides/schedule")
    suspend fun scheduleRide(@Body request: ScheduledRideRequestDto): Response<ScheduledRideResponseDto>
    
    @GET("rides/{rideId}")
    suspend fun getRideDetails(@Path("rideId") rideId: String): Response<RideResponseDto>
    
    @GET("rides/history")
    suspend fun getRideHistory(
        @Query("page") page: Int,
        @Query("page_size") pageSize: Int
    ): Response<List<RideResponseDto>>
    
    @POST("rides/{rideId}/cancel")
    suspend fun cancelRide(
        @Path("rideId") rideId: String,
        @Body request: CancelRideRequestDto
    ): Response<Unit>
    
    @POST("rides/{rideId}/accept")
    suspend fun acceptRide(@Path("rideId") rideId: String): Response<RideResponseDto>
    
    @POST("rides/{rideId}/reject")
    suspend fun rejectRide(
        @Path("rideId") rideId: String,
        @Body request: RejectRideRequestDto
    ): Response<Unit>
    
    @POST("rides/{rideId}/start")
    suspend fun startRide(@Path("rideId") rideId: String): Response<Unit>
    
    @POST("rides/{rideId}/complete")
    suspend fun completeRide(@Path("rideId") rideId: String): Response<Unit>
    
    @GET("rides/scheduled")
    suspend fun getScheduledRides(): Response<List<ScheduledRideResponseDto>>
    
    @POST("rides/scheduled/{rideId}/cancel")
    suspend fun cancelScheduledRide(@Path("rideId") rideId: String): Response<Unit>
}
