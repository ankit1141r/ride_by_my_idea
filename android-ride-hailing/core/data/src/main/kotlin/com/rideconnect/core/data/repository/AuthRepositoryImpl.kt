package com.rideconnect.core.data.repository

import com.rideconnect.core.common.result.Result
import com.rideconnect.core.data.local.TokenManagerWrapper
import com.rideconnect.core.data.mapper.toDomain
import com.rideconnect.core.domain.model.AuthToken
import com.rideconnect.core.domain.model.User
import com.rideconnect.core.domain.repository.AuthRepository
import com.rideconnect.core.network.api.AuthApi
import com.rideconnect.core.network.dto.RefreshTokenRequest
import com.rideconnect.core.network.dto.SendOtpRequest
import com.rideconnect.core.network.dto.VerifyOtpRequest
import kotlinx.coroutines.delay
import timber.log.Timber
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class AuthRepositoryImpl @Inject constructor(
    private val authApi: AuthApi,
    private val tokenManager: TokenManagerWrapper
) : AuthRepository {
    
    override suspend fun sendOtp(phoneNumber: String): Result<Unit> {
        return try {
            val response = authApi.sendOtp(SendOtpRequest(phoneNumber))
            if (response.isSuccessful) {
                Timber.d("OTP sent successfully to $phoneNumber")
                Result.Success(Unit)
            } else {
                val errorMessage = response.errorBody()?.string() ?: "Failed to send OTP"
                Timber.e("Failed to send OTP: $errorMessage")
                Result.Error(Exception(errorMessage))
            }
        } catch (e: Exception) {
            Timber.e(e, "Error sending OTP")
            Result.Error(e)
        }
    }
    
    override suspend fun verifyOtp(phoneNumber: String, otp: String): Result<Pair<AuthToken, User>> {
        return try {
            val response = authApi.verifyOtp(VerifyOtpRequest(phoneNumber, otp))
            if (response.isSuccessful && response.body() != null) {
                val authResponse = response.body()!!
                val authToken = AuthToken(
                    accessToken = authResponse.accessToken,
                    refreshToken = authResponse.refreshToken,
                    tokenType = authResponse.tokenType,
                    expiresIn = authResponse.expiresIn
                )
                val user = authResponse.user.toDomain()
                
                // Store token and user
                saveToken(authToken)
                saveUser(user)
                
                Timber.d("OTP verified successfully for $phoneNumber")
                Result.Success(Pair(authToken, user))
            } else {
                val errorMessage = response.errorBody()?.string() ?: "Failed to verify OTP"
                Timber.e("Failed to verify OTP: $errorMessage")
                Result.Error(Exception(errorMessage))
            }
        } catch (e: Exception) {
            Timber.e(e, "Error verifying OTP")
            Result.Error(e)
        }
    }
    
    override suspend fun refreshToken(refreshToken: String): Result<Pair<AuthToken, User>> {
        return try {
            val result = refreshTokenWithRetry(refreshToken, maxAttempts = 3)
            result
        } catch (e: Exception) {
            Timber.e(e, "Error refreshing token after retries")
            Result.Error(e)
        }
    }
    
    private suspend fun refreshTokenWithRetry(
        refreshToken: String,
        maxAttempts: Int,
        currentAttempt: Int = 1
    ): Result<Pair<AuthToken, User>> {
        return try {
            val response = authApi.refreshToken(RefreshTokenRequest(refreshToken))
            if (response.isSuccessful && response.body() != null) {
                val authResponse = response.body()!!
                val authToken = AuthToken(
                    accessToken = authResponse.accessToken,
                    refreshToken = authResponse.refreshToken,
                    tokenType = authResponse.tokenType,
                    expiresIn = authResponse.expiresIn
                )
                val user = authResponse.user.toDomain()
                
                // Store new token and user
                saveToken(authToken)
                saveUser(user)
                
                Timber.d("Token refreshed successfully")
                Result.Success(Pair(authToken, user))
            } else {
                val errorMessage = response.errorBody()?.string() ?: "Failed to refresh token"
                Timber.e("Failed to refresh token: $errorMessage")
                Result.Error(Exception(errorMessage))
            }
        } catch (e: Exception) {
            if (currentAttempt < maxAttempts) {
                val delayMs = calculateBackoffDelay(currentAttempt)
                Timber.w("Token refresh attempt $currentAttempt failed, retrying in ${delayMs}ms")
                delay(delayMs)
                refreshTokenWithRetry(refreshToken, maxAttempts, currentAttempt + 1)
            } else {
                Timber.e(e, "Token refresh failed after $maxAttempts attempts")
                Result.Error(e)
            }
        }
    }
    
    private fun calculateBackoffDelay(attempt: Int): Long {
        // Exponential backoff: 1s, 2s, 4s
        return (1000L * (1 shl (attempt - 1))).coerceAtMost(4000L)
    }
    
    override suspend fun logout(): Result<Unit> {
        return try {
            val response = authApi.logout()
            if (response.isSuccessful) {
                clearAll()
                Timber.d("Logout successful")
                Result.Success(Unit)
            } else {
                val errorMessage = response.errorBody()?.string() ?: "Failed to logout"
                Timber.e("Failed to logout: $errorMessage")
                // Clear local data even if API call fails
                clearAll()
                Result.Error(Exception(errorMessage))
            }
        } catch (e: Exception) {
            Timber.e(e, "Error during logout")
            // Clear local data even if API call fails
            clearAll()
            Result.Error(e)
        }
    }
    
    override fun getStoredToken(): AuthToken? {
        return tokenManager.getToken()
    }
    
    override fun getStoredUser(): User? {
        return tokenManager.getUser()
    }
    
    override suspend fun saveToken(token: AuthToken) {
        tokenManager.saveToken(token)
    }
    
    override suspend fun saveUser(user: User) {
        tokenManager.saveUser(user)
    }
    
    override suspend fun clearToken() {
        tokenManager.clearToken()
    }
    
    override suspend fun clearAll() {
        tokenManager.clearAll()
    }
}
