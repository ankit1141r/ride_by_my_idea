package com.rideconnect.core.network.api

import com.rideconnect.core.network.dto.AverageRatingResponseDto
import com.rideconnect.core.network.dto.RatingRequestDto
import com.rideconnect.core.network.dto.RatingResponseDto
import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.POST
import retrofit2.http.Path

interface RatingApi {
    
    @POST("ratings")
    suspend fun submitRating(@Body request: RatingRequestDto): Response<Unit>
    
    @GET("ratings/{userId}")
    suspend fun getRatings(@Path("userId") userId: String): Response<List<RatingResponseDto>>
    
    @GET("ratings/{userId}/average")
    suspend fun getAverageRating(@Path("userId") userId: String): Response<AverageRatingResponseDto>
}
