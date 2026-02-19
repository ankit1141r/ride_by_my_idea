package com.rideconnect.core.data.mapper

import com.rideconnect.core.domain.model.User
import com.rideconnect.core.domain.model.UserType
import com.rideconnect.core.network.dto.UserDto
import java.time.Instant

fun UserDto.toDomain(): User {
    return User(
        id = id,
        phoneNumber = phoneNumber,
        name = name,
        email = email,
        profilePhotoUrl = profilePhotoUrl,
        userType = when (userType.lowercase()) {
            "rider" -> UserType.RIDER
            "driver" -> UserType.DRIVER
            else -> UserType.RIDER
        },
        rating = rating,
        createdAt = try {
            Instant.parse(createdAt).toEpochMilli()
        } catch (e: Exception) {
            System.currentTimeMillis()
        }
    )
}
