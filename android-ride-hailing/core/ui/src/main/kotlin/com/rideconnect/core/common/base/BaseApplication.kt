package com.rideconnect.core.common.base

import android.app.Application
import android.content.Context
import android.content.res.Configuration
import com.rideconnect.core.ui.BuildConfig
import com.rideconnect.core.common.util.LanguageUtil
import com.rideconnect.core.common.util.StartupProfiler
import com.rideconnect.core.domain.model.Language

/**
 * Base Application class that handles language configuration and startup optimization
 * Requirements: 21.3, 21.4, 21.5, 23.1
 */
abstract class BaseApplication : Application() {
    
    override fun onCreate() {
        // Mark app start for profiling
        StartupProfiler.markAppStart()
        super.onCreate()
        
        // Record milestone after base initialization
        StartupProfiler.recordMilestone("Application.onCreate")
        
        // Initialize critical components
        initializeCriticalComponents()
        StartupProfiler.recordMilestone("Critical components initialized")
        
        // Initialize non-critical components asynchronously
        initializeNonCriticalComponents()
        
        // Log startup metrics in debug builds
        if (BuildConfig.DEBUG) {
            StartupProfiler.logStartupMetrics()
        }
    }
    
    override fun attachBaseContext(base: Context) {
        super.attachBaseContext(applyLanguage(base))
    }
    
    override fun onConfigurationChanged(newConfig: Configuration) {
        super.onConfigurationChanged(newConfig)
        // Handle device language changes
        // Requirements: 21.5
        applyLanguage(this)
    }
    
    /**
     * Apply saved language preference or use system default
     * Requirements: 21.3, 21.4
     */
    private fun applyLanguage(context: Context): Context {
        val language = getSavedLanguage()
        return LanguageUtil.applyLanguage(context, language)
    }
    
    /**
     * Initialize critical components that must be ready before UI is shown
     * Requirements: 23.1
     */
    protected open fun initializeCriticalComponents() {
        // Override in concrete implementations to initialize:
        // - Dependency injection (Hilt)
        // - Authentication state
        // - Language preferences
    }
    
    /**
     * Initialize non-critical components asynchronously
     * Requirements: 23.1
     */
    protected open fun initializeNonCriticalComponents() {
        // Override in concrete implementations to initialize:
        // - Analytics
        // - Crash reporting
        // - Image loading libraries
        // - Notification channels
    }
    
    /**
     * Get saved language preference from settings
     * Should be overridden by concrete implementations to access SettingsRepository
     */
    protected abstract fun getSavedLanguage(): Language
}
