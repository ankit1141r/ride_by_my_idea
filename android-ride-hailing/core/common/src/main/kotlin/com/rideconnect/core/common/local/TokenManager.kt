package com.rideconnect.core.common.local

import android.content.Context
import android.content.SharedPreferences
import androidx.security.crypto.EncryptedSharedPreferences
import androidx.security.crypto.MasterKey
import dagger.hilt.android.qualifiers.ApplicationContext
import timber.log.Timber
import javax.inject.Inject
import javax.inject.Singleton

/**
 * Simple token storage manager that stores tokens as strings.
 * Does not depend on domain models to avoid circular dependencies.
 */
@Singleton
class TokenManager @Inject constructor(
    @ApplicationContext private val context: Context
) {
    
    private val sharedPreferences: SharedPreferences by lazy {
        try {
            val masterKey = MasterKey.Builder(context)
                .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
                .build()

            EncryptedSharedPreferences.create(
                context,
                PREFS_NAME,
                masterKey,
                EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
                EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
            )
        } catch (e: Exception) {
            Timber.e(e, "Failed to create EncryptedSharedPreferences, falling back to regular SharedPreferences")
            context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
        }
    }
    
    fun saveAccessToken(token: String) {
        try {
            sharedPreferences.edit()
                .putString(KEY_ACCESS_TOKEN, token)
                .apply()
            Timber.d("Access token saved successfully")
        } catch (e: Exception) {
            Timber.e(e, "Failed to save access token")
        }
    }
    
    fun getAccessToken(): String? {
        return try {
            sharedPreferences.getString(KEY_ACCESS_TOKEN, null)
        } catch (e: Exception) {
            Timber.e(e, "Failed to get access token")
            null
        }
    }
    
    fun saveRefreshToken(token: String) {
        try {
            sharedPreferences.edit()
                .putString(KEY_REFRESH_TOKEN, token)
                .apply()
            Timber.d("Refresh token saved successfully")
        } catch (e: Exception) {
            Timber.e(e, "Failed to save refresh token")
        }
    }
    
    fun getRefreshToken(): String? {
        return try {
            sharedPreferences.getString(KEY_REFRESH_TOKEN, null)
        } catch (e: Exception) {
            Timber.e(e, "Failed to get refresh token")
            null
        }
    }
    
    fun saveUserId(userId: String) {
        try {
            sharedPreferences.edit()
                .putString(KEY_USER_ID, userId)
                .apply()
            Timber.d("User ID saved successfully")
        } catch (e: Exception) {
            Timber.e(e, "Failed to save user ID")
        }
    }
    
    fun getUserId(): String? {
        return try {
            sharedPreferences.getString(KEY_USER_ID, null)
        } catch (e: Exception) {
            Timber.e(e, "Failed to get user ID")
            null
        }
    }
    
    fun saveUserData(key: String, value: String) {
        try {
            sharedPreferences.edit()
                .putString(key, value)
                .apply()
            Timber.d("User data saved successfully: $key")
        } catch (e: Exception) {
            Timber.e(e, "Failed to save user data: $key")
        }
    }
    
    fun getUserData(key: String): String? {
        return try {
            sharedPreferences.getString(key, null)
        } catch (e: Exception) {
            Timber.e(e, "Failed to get user data: $key")
            null
        }
    }
    
    /**
     * Clear all stored authentication data
     * Requirements: 24.5
     * Note: For complete data clearing on logout, use DataCleaner which also clears
     * biometric keys, cache, and other sensitive data
     */
    fun clearAll() {
        try {
            sharedPreferences.edit()
                .clear()
                .apply()
            Timber.d("All tokens and user data cleared successfully")
        } catch (e: Exception) {
            Timber.e(e, "Failed to clear all data")
        }
    }
    
    companion object {
        private const val PREFS_NAME = "ride_connect_secure_prefs"
        private const val KEY_ACCESS_TOKEN = "access_token"
        private const val KEY_REFRESH_TOKEN = "refresh_token"
        private const val KEY_USER_ID = "user_id"
    }
}
