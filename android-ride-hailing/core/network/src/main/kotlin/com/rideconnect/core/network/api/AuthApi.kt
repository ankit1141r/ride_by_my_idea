package com.rideconnect.core.network.api

import com.rideconnect.core.network.dto.AuthResponse
import com.rideconnect.core.network.dto.RefreshTokenRequest
import com.rideconnect.core.network.dto.SendOtpRequest
import com.rideconnect.core.network.dto.VerifyOtpRequest
import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.POST

interface AuthApi {
    
    @POST("auth/send-otp")
    suspend fun sendOtp(@Body request: SendOtpRequest): Response<Unit>
    
    @POST("auth/verify-otp")
    suspend fun verifyOtp(@Body request: VerifyOtpRequest): Response<AuthResponse>
    
    @POST("auth/refresh")
    suspend fun refreshToken(@Body request: RefreshTokenRequest): Response<AuthResponse>
    
    @POST("auth/logout")
    suspend fun logout(): Response<Unit>
}
