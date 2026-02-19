package com.rideconnect.core.network.api

import com.rideconnect.core.network.dto.EmergencyContactRequestDto
import com.rideconnect.core.network.dto.EmergencyContactResponseDto
import com.rideconnect.core.network.dto.SOSRequestDto
import com.rideconnect.core.network.dto.ShareRideRequestDto
import com.rideconnect.core.network.dto.ShareRideResponseDto
import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.DELETE
import retrofit2.http.GET
import retrofit2.http.POST
import retrofit2.http.Path

interface EmergencyApi {
    
    @POST("emergency/sos")
    suspend fun triggerSOS(@Body request: SOSRequestDto): Response<Unit>
    
    @GET("emergency/contacts")
    suspend fun getEmergencyContacts(): Response<List<EmergencyContactResponseDto>>
    
    @POST("emergency/contacts")
    suspend fun addEmergencyContact(@Body request: EmergencyContactRequestDto): Response<EmergencyContactResponseDto>
    
    @DELETE("emergency/contacts/{contactId}")
    suspend fun removeEmergencyContact(@Path("contactId") contactId: String): Response<Unit>
    
    @POST("emergency/share-ride")
    suspend fun shareRide(@Body request: ShareRideRequestDto): Response<ShareRideResponseDto>
}
