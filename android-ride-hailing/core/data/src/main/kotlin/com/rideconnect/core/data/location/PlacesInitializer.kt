package com.rideconnect.core.data.location

import android.content.Context
import com.google.android.libraries.places.api.Places
import dagger.hilt.android.qualifiers.ApplicationContext
import timber.log.Timber
import javax.inject.Inject
import javax.inject.Singleton

/**
 * Initializer for Google Places SDK.
 * Must be called once during app startup.
 * 
 * Requirements: 18.3, 18.4
 */
@Singleton
class PlacesInitializer @Inject constructor(
    @ApplicationContext private val context: Context
) {
    
    /**
     * Initialize Google Places SDK with API key.
     * API key should be stored in local.properties or BuildConfig.
     * 
     * Note: In production, the API key should be:
     * 1. Stored in local.properties (not committed to version control)
     * 2. Loaded via BuildConfig
     * 3. Restricted in Google Cloud Console to specific package name and SHA-1
     */
    fun initialize(apiKey: String) {
        if (!Places.isInitialized()) {
            try {
                Places.initialize(context, apiKey)
                Timber.d("Google Places SDK initialized successfully")
            } catch (e: Exception) {
                Timber.e(e, "Failed to initialize Google Places SDK")
                throw e
            }
        } else {
            Timber.d("Google Places SDK already initialized")
        }
    }
    
    /**
     * Check if Places SDK is initialized.
     */
    fun isInitialized(): Boolean {
        return Places.isInitialized()
    }
}
