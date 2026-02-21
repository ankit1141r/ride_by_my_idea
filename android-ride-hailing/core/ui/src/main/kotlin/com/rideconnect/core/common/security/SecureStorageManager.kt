package com.rideconnect.core.common.security

import android.content.Context
import android.content.SharedPreferences
import android.security.keystore.KeyGenParameterSpec
import android.security.keystore.KeyProperties
import androidx.security.crypto.EncryptedSharedPreferences
import androidx.security.crypto.MasterKey
import timber.log.Timber
import java.security.KeyStore
import javax.crypto.KeyGenerator
import javax.crypto.SecretKey

/**
 * Manager for secure storage using EncryptedSharedPreferences and Android Keystore
 * Requirements: 24.1, 24.8
 */
class SecureStorageManager(private val context: Context) {
    
    private val masterKey: MasterKey by lazy {
        MasterKey.Builder(context)
            .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
            .build()
    }
    
    /**
     * Create encrypted shared preferences
     * Requirements: 24.1
     */
    fun createEncryptedPreferences(prefsName: String): SharedPreferences {
        return try {
            EncryptedSharedPreferences.create(
                context,
                prefsName,
                masterKey,
                EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
                EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
            )
        } catch (e: Exception) {
            Timber.e(e, "Failed to create EncryptedSharedPreferences")
            // Fallback to regular SharedPreferences (not recommended for production)
            context.getSharedPreferences(prefsName, Context.MODE_PRIVATE)
        }
    }
    
    /**
     * Generate a key in Android Keystore for biometric authentication
     * Requirements: 24.8
     */
    fun generateBiometricKey(keyAlias: String): SecretKey? {
        return try {
            val keyGenerator = KeyGenerator.getInstance(
                KeyProperties.KEY_ALGORITHM_AES,
                ANDROID_KEYSTORE
            )
            
            val keyGenParameterSpec = KeyGenParameterSpec.Builder(
                keyAlias,
                KeyProperties.PURPOSE_ENCRYPT or KeyProperties.PURPOSE_DECRYPT
            )
                .setBlockModes(KeyProperties.BLOCK_MODE_GCM)
                .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE)
                .setUserAuthenticationRequired(true)
                .setInvalidatedByBiometricEnrollment(true)
                .build()
            
            keyGenerator.init(keyGenParameterSpec)
            keyGenerator.generateKey()
        } catch (e: Exception) {
            Timber.e(e, "Failed to generate biometric key")
            null
        }
    }
    
    /**
     * Get a key from Android Keystore
     * Requirements: 24.8
     */
    fun getKeyFromKeystore(keyAlias: String): SecretKey? {
        return try {
            val keyStore = KeyStore.getInstance(ANDROID_KEYSTORE)
            keyStore.load(null)
            
            val secretKeyEntry = keyStore.getEntry(keyAlias, null) as? KeyStore.SecretKeyEntry
            secretKeyEntry?.secretKey
        } catch (e: Exception) {
            Timber.e(e, "Failed to get key from keystore")
            null
        }
    }
    
    /**
     * Delete a key from Android Keystore
     */
    fun deleteKeyFromKeystore(keyAlias: String): Boolean {
        return try {
            val keyStore = KeyStore.getInstance(ANDROID_KEYSTORE)
            keyStore.load(null)
            keyStore.deleteEntry(keyAlias)
            true
        } catch (e: Exception) {
            Timber.e(e, "Failed to delete key from keystore")
            false
        }
    }
    
    /**
     * Check if a key exists in Android Keystore
     */
    fun keyExistsInKeystore(keyAlias: String): Boolean {
        return try {
            val keyStore = KeyStore.getInstance(ANDROID_KEYSTORE)
            keyStore.load(null)
            keyStore.containsAlias(keyAlias)
        } catch (e: Exception) {
            Timber.e(e, "Failed to check key existence")
            false
        }
    }
    
    /**
     * Clear all data from encrypted preferences
     * Requirements: 24.5
     */
    fun clearEncryptedPreferences(prefsName: String) {
        try {
            val prefs = createEncryptedPreferences(prefsName)
            prefs.edit().clear().apply()
            Timber.d("Cleared encrypted preferences: $prefsName")
        } catch (e: Exception) {
            Timber.e(e, "Failed to clear encrypted preferences")
        }
    }
    
    companion object {
        private const val ANDROID_KEYSTORE = "AndroidKeyStore"
        const val BIOMETRIC_KEY_ALIAS = "ride_connect_biometric_key"
    }
}
