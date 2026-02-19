package com.rideconnect.core.network.api

import com.rideconnect.core.network.dto.ParcelDeliveryRequestDto
import com.rideconnect.core.network.dto.ParcelDeliveryResponseDto
import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.POST
import retrofit2.http.Path
import retrofit2.http.Query

interface ParcelApi {
    
    @POST("parcels/request")
    suspend fun requestParcelDelivery(@Body request: ParcelDeliveryRequestDto): Response<ParcelDeliveryResponseDto>
    
    @POST("parcels/{deliveryId}/pickup")
    suspend fun confirmPickup(@Path("deliveryId") deliveryId: String): Response<Unit>
    
    @POST("parcels/{deliveryId}/deliver")
    suspend fun confirmDelivery(@Path("deliveryId") deliveryId: String): Response<Unit>
    
    @GET("parcels/history")
    suspend fun getParcelHistory(
        @Query("page") page: Int,
        @Query("page_size") pageSize: Int
    ): Response<List<ParcelDeliveryResponseDto>>
}
