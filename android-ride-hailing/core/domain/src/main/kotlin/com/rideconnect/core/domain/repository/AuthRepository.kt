package com.rideconnect.core.domain.repository

import com.rideconnect.core.domain.model.AuthToken
import com.rideconnect.core.domain.model.User

interface AuthRepository {
    suspend fun sendOtp(phoneNumber: String): Result<Unit>
    suspend fun verifyOtp(phoneNumber: String, otp: String): Result<Pair<AuthToken, User>>
    suspend fun refreshToken(refreshToken: String): Result<Pair<AuthToken, User>>
    suspend fun logout(): Result<Unit>
    fun getStoredToken(): AuthToken?
    fun getStoredUser(): User?
    suspend fun saveToken(token: AuthToken)
    suspend fun saveUser(user: User)
    suspend fun clearToken()
    suspend fun clearAll()
}
