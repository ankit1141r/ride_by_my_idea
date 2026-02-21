package com.rideconnect.core.common.security

import android.content.Context
import timber.log.Timber

/**
 * Utility for clearing sensitive data on logout
 * Requirements: 24.5
 */
class DataCleaner(
    private val context: Context,
    private val secureStorageManager: SecureStorageManager
) {
    
    /**
     * Clear all sensitive data on logout
     * Requirements: 24.5
     */
    fun clearAllSensitiveData() {
        Timber.d("Clearing all sensitive data on logout")
        
        try {
            // Clear authentication tokens
            clearAuthenticationData()
            
            // Clear cached user data
            clearUserCache()
            
            // Clear biometric keys
            clearBiometricData()
            
            // Clear any in-memory sensitive data
            clearMemoryData()
            
            Timber.d("Successfully cleared all sensitive data")
        } catch (e: Exception) {
            Timber.e(e, "Error clearing sensitive data")
        }
    }
    
    /**
     * Clear authentication tokens and credentials
     * Requirements: 24.5
     */
    private fun clearAuthenticationData() {
        // Clear encrypted preferences containing tokens
        secureStorageManager.clearEncryptedPreferences(PREFS_AUTH)
        secureStorageManager.clearEncryptedPreferences(PREFS_USER)
        
        // Clear regular shared preferences
        context.getSharedPreferences(PREFS_SETTINGS, Context.MODE_PRIVATE)
            .edit()
            .remove(KEY_USER_ID)
            .remove(KEY_USER_TYPE)
            .apply()
        
        Timber.d("Cleared authentication data")
    }
    
    /**
     * Clear cached user data
     * Requirements: 24.5
     */
    private fun clearUserCache() {
        // Clear user-related preferences
        val userPrefs = context.getSharedPreferences(PREFS_USER_CACHE, Context.MODE_PRIVATE)
        userPrefs.edit().clear().apply()
        
        // Note: Room database should be cleared by repository layer
        // This is just for SharedPreferences cache
        
        Timber.d("Cleared user cache")
    }
    
    /**
     * Clear biometric authentication data
     * Requirements: 24.5, 24.8
     */
    private fun clearBiometricData() {
        // Delete biometric key from Android Keystore
        secureStorageManager.deleteKeyFromKeystore(SecureStorageManager.BIOMETRIC_KEY_ALIAS)
        
        // Clear biometric preferences
        secureStorageManager.clearEncryptedPreferences(PREFS_BIOMETRIC)
        
        Timber.d("Cleared biometric data")
    }
    
    /**
     * Clear sensitive data from memory
     * Requirements: 24.5
     */
    private fun clearMemoryData() {
        // Force garbage collection to clear sensitive data from memory
        // Note: This is a hint to the JVM, not guaranteed
        System.gc()
        
        Timber.d("Requested memory cleanup")
    }
    
    /**
     * Clear specific preference file
     */
    fun clearPreferences(prefsName: String) {
        try {
            context.getSharedPreferences(prefsName, Context.MODE_PRIVATE)
                .edit()
                .clear()
                .apply()
            Timber.d("Cleared preferences: $prefsName")
        } catch (e: Exception) {
            Timber.e(e, "Error clearing preferences: $prefsName")
        }
    }
    
    /**
     * Clear app cache directory
     */
    fun clearAppCache() {
        try {
            context.cacheDir.deleteRecursively()
            Timber.d("Cleared app cache directory")
        } catch (e: Exception) {
            Timber.e(e, "Error clearing app cache")
        }
    }
    
    /**
     * Verify all sensitive data has been cleared
     * Returns true if all checks pass
     */
    fun verifySensitiveDataCleared(): Boolean {
        try {
            // Check if auth tokens are cleared
            val authPrefs = secureStorageManager.createEncryptedPreferences(PREFS_AUTH)
            val hasAuthData = authPrefs.all.isNotEmpty()
            
            // Check if biometric key is deleted
            val hasBiometricKey = secureStorageManager.keyExistsInKeystore(
                SecureStorageManager.BIOMETRIC_KEY_ALIAS
            )
            
            val isCleared = !hasAuthData && !hasBiometricKey
            
            if (isCleared) {
                Timber.d("Verification passed: All sensitive data cleared")
            } else {
                Timber.w("Verification failed: Some sensitive data remains")
            }
            
            return isCleared
        } catch (e: Exception) {
            Timber.e(e, "Error verifying data clearance")
            return false
        }
    }
    
    companion object {
        // Preference file names
        private const val PREFS_AUTH = "auth_prefs"
        private const val PREFS_USER = "user_prefs"
        private const val PREFS_BIOMETRIC = "biometric_prefs"
        private const val PREFS_SETTINGS = "settings_prefs"
        private const val PREFS_USER_CACHE = "user_cache_prefs"
        
        // Preference keys
        private const val KEY_USER_ID = "user_id"
        private const val KEY_USER_TYPE = "user_type"
    }
}
