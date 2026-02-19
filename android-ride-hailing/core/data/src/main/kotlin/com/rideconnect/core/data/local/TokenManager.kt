package com.rideconnect.core.data.local

import android.content.Context
import android.content.SharedPreferences
import androidx.security.crypto.EncryptedSharedPreferences
import androidx.security.crypto.MasterKey
import com.google.gson.Gson
import com.rideconnect.core.domain.model.AuthToken
import com.rideconnect.core.domain.model.User
import dagger.hilt.android.qualifiers.ApplicationContext
import timber.log.Timber
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class TokenManager @Inject constructor(
    @ApplicationContext private val context: Context,
    private val gson: Gson
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
    
    fun saveToken(token: AuthToken) {
        try {
            val tokenJson = gson.toJson(token)
            sharedPreferences.edit()
                .putString(KEY_AUTH_TOKEN, tokenJson)
                .apply()
            Timber.d("Token saved successfully")
        } catch (e: Exception) {
            Timber.e(e, "Failed to save token")
        }
    }
    
    fun getToken(): AuthToken? {
        return try {
            val tokenJson = sharedPreferences.getString(KEY_AUTH_TOKEN, null)
            if (tokenJson != null) {
                gson.fromJson(tokenJson, AuthToken::class.java)
            } else {
                null
            }
        } catch (e: Exception) {
            Timber.e(e, "Failed to get token")
            null
        }
    }
    
    fun clearToken() {
        try {
            sharedPreferences.edit()
                .remove(KEY_AUTH_TOKEN)
                .apply()
            Timber.d("Token cleared successfully")
        } catch (e: Exception) {
            Timber.e(e, "Failed to clear token")
        }
    }
    
    fun saveUser(user: User) {
        try {
            val userJson = gson.toJson(user)
            sharedPreferences.edit()
                .putString(KEY_USER, userJson)
                .apply()
            Timber.d("User saved successfully")
        } catch (e: Exception) {
            Timber.e(e, "Failed to save user")
        }
    }
    
    fun getUser(): User? {
        return try {
            val userJson = sharedPreferences.getString(KEY_USER, null)
            if (userJson != null) {
                gson.fromJson(userJson, User::class.java)
            } else {
                null
            }
        } catch (e: Exception) {
            Timber.e(e, "Failed to get user")
            null
        }
    }
    
    fun clearUser() {
        try {
            sharedPreferences.edit()
                .remove(KEY_USER)
                .apply()
            Timber.d("User cleared successfully")
        } catch (e: Exception) {
            Timber.e(e, "Failed to clear user")
        }
    }
    
    fun clearAll() {
        clearToken()
        clearUser()
    }
    
    companion object {
        private const val PREFS_NAME = "ride_connect_secure_prefs"
        private const val KEY_AUTH_TOKEN = "auth_token"
        private const val KEY_USER = "user"
    }
}
