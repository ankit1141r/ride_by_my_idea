package com.rideconnect.core.domain.model

data class ProfileUpdateRequest(
    val name: String? = null,
    val email: String? = null,
    val profilePhotoUrl: String? = null
)
