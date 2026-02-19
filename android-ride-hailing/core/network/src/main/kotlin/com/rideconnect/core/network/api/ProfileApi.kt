package com.rideconnect.core.network.api

import com.rideconnect.core.network.dto.*
import okhttp3.MultipartBody
import retrofit2.Response
import retrofit2.http.*

interface ProfileApi {
    
    @PUT("/api/profile")
    suspend fun updateProfile(
        @Body request: ProfileUpdateRequestDto
    ): Response<UserDto>
    
    @Multipart
    @POST("/api/profile/photo")
    suspend fun uploadProfilePhoto(
        @Part photo: MultipartBody.Part
    ): Response<ProfilePhotoUploadResponse>
    
    @GET("/api/profile")
    suspend fun getProfile(): Response<UserDto>
    
    @PUT("/api/drivers/vehicle")
    suspend fun updateVehicleDetails(
        @Body request: VehicleUpdateRequestDto
    ): Response<VehicleDetailsDto>
    
    @GET("/api/drivers/vehicle")
    suspend fun getVehicleDetails(): Response<VehicleDetailsDto>
    
    @GET("/api/emergency-contacts")
    suspend fun getEmergencyContacts(): Response<List<EmergencyContactDto>>
    
    @POST("/api/emergency-contacts")
    suspend fun addEmergencyContact(
        @Body request: EmergencyContactRequestDto
    ): Response<EmergencyContactDto>
    
    @DELETE("/api/emergency-contacts/{contactId}")
    suspend fun removeEmergencyContact(
        @Path("contactId") contactId: String
    ): Response<Unit>
}
