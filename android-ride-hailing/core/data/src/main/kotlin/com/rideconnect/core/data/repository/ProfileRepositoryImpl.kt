package com.rideconnect.core.data.repository

import android.content.Context
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import com.rideconnect.core.common.result.Result
import com.rideconnect.core.domain.model.EmergencyContact
import com.rideconnect.core.domain.model.ProfileUpdateRequest
import com.rideconnect.core.domain.model.User
import com.rideconnect.core.domain.model.UserType
import com.rideconnect.core.domain.model.VehicleDetails
import com.rideconnect.core.domain.model.VehicleType
import com.rideconnect.core.domain.repository.ProfileRepository
import com.rideconnect.core.network.api.ProfileApi
import com.rideconnect.core.network.dto.EmergencyContactRequestDto
import com.rideconnect.core.network.dto.ProfileUpdateRequestDto
import com.rideconnect.core.network.dto.VehicleUpdateRequestDto
import dagger.hilt.android.qualifiers.ApplicationContext
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import okhttp3.MediaType.Companion.toMediaTypeOrNull
import okhttp3.MultipartBody
import okhttp3.RequestBody.Companion.asRequestBody
import java.io.File
import java.io.FileOutputStream
import java.time.Instant
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class ProfileRepositoryImpl @Inject constructor(
    @ApplicationContext private val context: Context,
    private val profileApi: ProfileApi
) : ProfileRepository {
    
    companion object {
        private const val MAX_IMAGE_WIDTH = 1024
        private const val MAX_IMAGE_HEIGHT = 1024
        private const val COMPRESSION_QUALITY = 80
    }
    
    override suspend fun updateProfile(request: ProfileUpdateRequest): Result<User> {
        return try {
            val requestDto = ProfileUpdateRequestDto(
                name = request.name,
                email = request.email,
                profilePhotoUrl = request.profilePhotoUrl
            )
            
            val response = profileApi.updateProfile(requestDto)
            
            if (response.isSuccessful && response.body() != null) {
                val userDto = response.body()!!
                val user = User(
                    id = userDto.id,
                    phoneNumber = userDto.phoneNumber,
                    name = userDto.name,
                    email = userDto.email,
                    profilePhotoUrl = userDto.profilePhotoUrl,
                    userType = UserType.valueOf(userDto.userType.uppercase()),
                    rating = userDto.rating,
                    createdAt = Instant.parse(userDto.createdAt).toEpochMilli()
                )
                Result.Success(user)
            } else {
                Result.Error(Exception("Failed to update profile: ${response.message()}"))
            }
        } catch (e: Exception) {
            Result.Error(e)
        }
    }
    
    override suspend fun uploadProfilePhoto(photoFile: File): Result<String> {
        return try {
            // Compress image before upload
            val compressedFile = compressImage(photoFile)
            
            val requestBody = compressedFile.asRequestBody("image/jpeg".toMediaTypeOrNull())
            val multipartBody = MultipartBody.Part.createFormData(
                "photo",
                compressedFile.name,
                requestBody
            )
            
            val response = profileApi.uploadProfilePhoto(multipartBody)
            
            // Clean up compressed file
            compressedFile.delete()
            
            if (response.isSuccessful && response.body() != null) {
                Result.Success(response.body()!!.photoUrl)
            } else {
                Result.Error(Exception("Failed to upload photo: ${response.message()}"))
            }
        } catch (e: Exception) {
            Result.Error(e)
        }
    }
    
    override suspend fun getProfile(): Result<User> {
        return try {
            val response = profileApi.getProfile()
            
            if (response.isSuccessful && response.body() != null) {
                val userDto = response.body()!!
                val user = User(
                    id = userDto.id,
                    phoneNumber = userDto.phoneNumber,
                    name = userDto.name,
                    email = userDto.email,
                    profilePhotoUrl = userDto.profilePhotoUrl,
                    userType = UserType.valueOf(userDto.userType.uppercase()),
                    rating = userDto.rating,
                    createdAt = Instant.parse(userDto.createdAt).toEpochMilli()
                )
                Result.Success(user)
            } else {
                Result.Error(Exception("Failed to get profile: ${response.message()}"))
            }
        } catch (e: Exception) {
            Result.Error(e)
        }
    }
    
    override suspend fun updateVehicleDetails(
        vehicleDetails: VehicleDetails,
        licenseNumber: String
    ): Result<VehicleDetails> {
        return try {
            val requestDto = VehicleUpdateRequestDto(
                make = vehicleDetails.make,
                model = vehicleDetails.model,
                year = vehicleDetails.year,
                color = vehicleDetails.color,
                licensePlate = vehicleDetails.licensePlate,
                vehicleType = vehicleDetails.vehicleType.name.lowercase(),
                licenseNumber = licenseNumber
            )
            
            val response = profileApi.updateVehicleDetails(requestDto)
            
            if (response.isSuccessful && response.body() != null) {
                val dto = response.body()!!
                val vehicle = VehicleDetails(
                    make = dto.make,
                    model = dto.model,
                    year = dto.year,
                    color = dto.color,
                    licensePlate = dto.licensePlate,
                    vehicleType = VehicleType.valueOf(dto.vehicleType.uppercase())
                )
                Result.Success(vehicle)
            } else {
                Result.Error(Exception("Failed to update vehicle details: ${response.message()}"))
            }
        } catch (e: Exception) {
            Result.Error(e)
        }
    }
    
    override suspend fun getVehicleDetails(): Result<VehicleDetails> {
        return try {
            val response = profileApi.getVehicleDetails()
            
            if (response.isSuccessful && response.body() != null) {
                val dto = response.body()!!
                val vehicle = VehicleDetails(
                    make = dto.make,
                    model = dto.model,
                    year = dto.year,
                    color = dto.color,
                    licensePlate = dto.licensePlate,
                    vehicleType = VehicleType.valueOf(dto.vehicleType.uppercase())
                )
                Result.Success(vehicle)
            } else {
                Result.Error(Exception("Failed to get vehicle details: ${response.message()}"))
            }
        } catch (e: Exception) {
            Result.Error(e)
        }
    }
    
    override suspend fun getEmergencyContacts(): Result<List<EmergencyContact>> {
        return try {
            val response = profileApi.getEmergencyContacts()
            
            if (response.isSuccessful && response.body() != null) {
                val contacts = response.body()!!.map { dto ->
                    EmergencyContact(
                        id = dto.id,
                        name = dto.name,
                        phoneNumber = dto.phoneNumber,
                        relationship = dto.relationship
                    )
                }
                Result.Success(contacts)
            } else {
                Result.Error(Exception("Failed to get emergency contacts: ${response.message()}"))
            }
        } catch (e: Exception) {
            Result.Error(e)
        }
    }
    
    override suspend fun addEmergencyContact(contact: EmergencyContact): Result<EmergencyContact> {
        return try {
            val requestDto = EmergencyContactRequestDto(
                name = contact.name,
                phoneNumber = contact.phoneNumber,
                relationship = contact.relationship
            )
            
            val response = profileApi.addEmergencyContact(requestDto)
            
            if (response.isSuccessful && response.body() != null) {
                val dto = response.body()!!
                val newContact = EmergencyContact(
                    id = dto.id,
                    name = dto.name,
                    phoneNumber = dto.phoneNumber,
                    relationship = dto.relationship
                )
                Result.Success(newContact)
            } else {
                Result.Error(Exception("Failed to add emergency contact: ${response.message()}"))
            }
        } catch (e: Exception) {
            Result.Error(e)
        }
    }
    
    override suspend fun removeEmergencyContact(contactId: String): Result<Unit> {
        return try {
            val response = profileApi.removeEmergencyContact(contactId)
            
            if (response.isSuccessful) {
                Result.Success(Unit)
            } else {
                Result.Error(Exception("Failed to remove emergency contact: ${response.message()}"))
            }
        } catch (e: Exception) {
            Result.Error(e)
        }
    }
    
    /**
     * Compresses an image file to reduce size before upload.
     * Target: At least 50% size reduction while maintaining quality.
     */
    private suspend fun compressImage(originalFile: File): File = withContext(Dispatchers.IO) {
        val bitmap = BitmapFactory.decodeFile(originalFile.absolutePath)
        
        // Calculate scaled dimensions
        val (scaledWidth, scaledHeight) = calculateScaledDimensions(
            bitmap.width,
            bitmap.height,
            MAX_IMAGE_WIDTH,
            MAX_IMAGE_HEIGHT
        )
        
        // Scale bitmap if needed
        val scaledBitmap = if (scaledWidth != bitmap.width || scaledHeight != bitmap.height) {
            Bitmap.createScaledBitmap(bitmap, scaledWidth, scaledHeight, true)
        } else {
            bitmap
        }
        
        // Create compressed file
        val compressedFile = File(context.cacheDir, "compressed_${System.currentTimeMillis()}.jpg")
        FileOutputStream(compressedFile).use { out ->
            scaledBitmap.compress(Bitmap.CompressFormat.JPEG, COMPRESSION_QUALITY, out)
        }
        
        // Clean up bitmaps
        if (scaledBitmap != bitmap) {
            scaledBitmap.recycle()
        }
        bitmap.recycle()
        
        compressedFile
    }
    
    private fun calculateScaledDimensions(
        width: Int,
        height: Int,
        maxWidth: Int,
        maxHeight: Int
    ): Pair<Int, Int> {
        if (width <= maxWidth && height <= maxHeight) {
            return Pair(width, height)
        }
        
        val widthRatio = maxWidth.toFloat() / width
        val heightRatio = maxHeight.toFloat() / height
        val ratio = minOf(widthRatio, heightRatio)
        
        return Pair(
            (width * ratio).toInt(),
            (height * ratio).toInt()
        )
    }
}
