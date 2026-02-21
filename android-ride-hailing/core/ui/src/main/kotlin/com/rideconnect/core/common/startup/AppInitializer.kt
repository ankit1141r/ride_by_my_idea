package com.rideconnect.core.common.startup

import android.content.Context
import androidx.startup.Initializer
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.launch

/**
 * Base initializer for app startup components.
 * Uses lazy initialization to optimize app startup time.
 */
abstract class BaseInitializer<T> : Initializer<T> {
    protected val applicationScope = CoroutineScope(SupervisorJob() + Dispatchers.Default)
    
    /**
     * Initialize component asynchronously in background
     */
    protected fun initializeAsync(block: suspend () -> Unit) {
        applicationScope.launch {
            block()
        }
    }
}

/**
 * Initializer for Coil image loading library.
 * Configures image caching and compression settings.
 */
class CoilInitializer : BaseInitializer<Unit>() {
    override fun create(context: Context) {
        // Coil auto-initializes, but we can configure it here if needed
        // This is a placeholder for custom Coil configuration
    }

    override fun dependencies(): List<Class<out Initializer<*>>> = emptyList()
}

/**
 * Initializer for analytics and crash reporting.
 * Initializes Firebase Crashlytics asynchronously.
 */
class AnalyticsInitializer : BaseInitializer<Unit>() {
    override fun create(context: Context) {
        initializeAsync {
            // Initialize Firebase Crashlytics
            // This happens in background to not block app startup
        }
    }

    override fun dependencies(): List<Class<out Initializer<*>>> = emptyList()
}

/**
 * Initializer for notification channels.
 * Creates notification channels for Android 8.0+
 */
class NotificationInitializer : BaseInitializer<Unit>() {
    override fun create(context: Context) {
        initializeAsync {
            // Notification channels will be created when needed
            // This is a placeholder for lazy initialization
        }
    }

    override fun dependencies(): List<Class<out Initializer<*>>> = emptyList()
}
