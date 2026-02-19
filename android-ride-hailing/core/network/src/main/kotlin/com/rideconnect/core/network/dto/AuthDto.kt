package com.rideconnect.core.network.dto

import com.google.gson.annotations.SerializedName

data class SendOtpRequest(
    @SerializedName("phone_number")
    val phoneNumber: String
)

data class VerifyOtpRequest(
    @SerializedName("phone_number")
    val phoneNumber: String,
    @SerializedName("otp")
    val otp: String
)

data class RefreshTokenRequest(
    @SerializedName("refresh_token")
    val refreshToken: String
)

data class AuthResponse(
    @SerializedName("access_token")
    val accessToken: String,
    @SerializedName("refresh_token")
    val refreshToken: String,
    @SerializedName("token_type")
    val tokenType: String,
    @SerializedName("expires_in")
    val expiresIn: Long?,
    @SerializedName("user")
    val user: UserDto
)

data class UserDto(
    @SerializedName("id")
    val id: String,
    @SerializedName("phone_number")
    val phoneNumber: String,
    @SerializedName("name")
    val name: String,
    @SerializedName("email")
    val email: String?,
    @SerializedName("profile_photo_url")
    val profilePhotoUrl: String?,
    @SerializedName("user_type")
    val userType: String,
    @SerializedName("rating")
    val rating: Double,
    @SerializedName("created_at")
    val createdAt: String
)
