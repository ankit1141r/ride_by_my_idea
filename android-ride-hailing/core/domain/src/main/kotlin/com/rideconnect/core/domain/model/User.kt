package com.rideconnect.core.domain.model

data class User(
    val id: String,
    val phoneNumber: String,
    val name: String,
    val email: String? = null,
    val profilePhotoUrl: String? = null,
    val userType: UserType,
    val rating: Double = 0.0,
    val createdAt: Long
)

enum class UserType {
    RIDER,
    DRIVER
}
