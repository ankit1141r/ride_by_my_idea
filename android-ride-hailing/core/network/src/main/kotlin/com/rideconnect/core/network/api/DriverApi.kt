package com.rideconnect.core.network.api

import com.rideconnect.core.network.dto.AvailabilityRequestDto
import com.rideconnect.core.network.dto.EarningsResponseDto
import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.POST
import retrofit2.http.Query

interface DriverApi {
    
    @POST("drivers/availability")
    suspend fun setAvailability(@Body request: AvailabilityRequestDto): Response<Unit>
    
    @GET("drivers/earnings")
    suspend fun getEarnings(
        @Query("start_date") startDate: String,
        @Query("end_date") endDate: String
    ): Response<EarningsResponseDto>
}
