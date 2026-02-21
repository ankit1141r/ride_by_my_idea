package com.rideconnect.core.data.local

import com.google.gson.Gson
import com.rideconnect.core.common.local.TokenManager
import com.rideconnect.core.domain.model.AuthToken
import com.rideconnect.core.domain.model.User
import javax.inject.Inject
import javax.inject.Singleton

/**
 * Wrapper around TokenManager that provides domain model support.
 * This allows repositories to work with domain models while TokenManager
 * remains independent of domain layer.
 */
@Singleton
class TokenManagerWrapper @Inject constructor(
    private val tokenManager: TokenManager,
    private val gson: Gson
) {
    
    fun saveToken(token: AuthToken) {
        tokenManager.saveAccessToken(token.accessToken)
        tokenManager.saveRefreshToken(token.refreshToken)
    }
    
    fun getToken(): AuthToken? {
        val accessToken = tokenManager.getAccessToken() ?: return null
        val refreshToken = tokenManager.getRefreshToken() ?: return null
        return AuthToken(accessToken, refreshToken)
    }
    
    fun clearToken() {
        tokenManager.saveAccessToken("")
        tokenManager.saveRefreshToken("")
    }
    
    fun saveUser(user: User) {
        val userJson = gson.toJson(user)
        tokenManager.saveUserData("user", userJson)
        tokenManager.saveUserId(user.id)
    }
    
    fun getUser(): User? {
        val userJson = tokenManager.getUserData("user") ?: return null
        return try {
            gson.fromJson(userJson, User::class.java)
        } catch (e: Exception) {
            null
        }
    }
    
    fun clearUser() {
        tokenManager.saveUserData("user", "")
        tokenManager.saveUserId("")
    }
    
    fun clearAll() {
        tokenManager.clearAll()
    }
    
    fun getUserId(): String? {
        return tokenManager.getUserId()
    }
}
