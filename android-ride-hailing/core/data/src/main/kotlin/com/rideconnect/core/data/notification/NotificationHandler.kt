package com.rideconnect.core.data.notification

import android.content.Context
import android.content.Intent
import androidx.core.net.toUri
import dagger.hilt.android.qualifiers.ApplicationContext
import javax.inject.Inject
import javax.inject.Singleton

/**
 * Handler for processing notifications and creating deep links.
 * Requirements: 19.3, 19.4, 19.5, 19.6, 19.7, 19.8
 */
@Singleton
class NotificationHandler @Inject constructor(
    @ApplicationContext private val context: Context,
    private val notificationPreferences: NotificationPreferences
) {
    
    /**
     * Handle incoming notification and determine if it should be shown.
     * Requirements: 19.7
     */
    fun shouldShowNotification(type: NotificationType): Boolean {
        return notificationPreferences.isNotificationEnabled(type)
    }
    
    /**
     * Create deep link intent for notification.
     * Requirements: 19.8
     */
    fun createDeepLinkIntent(
        type: NotificationType,
        data: Map<String, String>
    ): Intent {
        val deepLink = when (type) {
            NotificationType.RIDE_REQUEST -> {
                val rideId = data["ride_id"] ?: ""
                "rideconnect://ride/$rideId"
            }
            NotificationType.RIDE_ACCEPTED,
            NotificationType.RIDE_STARTED,
            NotificationType.RIDE_COMPLETED,
            NotificationType.RIDE_CANCELLED -> {
                val rideId = data["ride_id"] ?: ""
                "rideconnect://ride/tracking/$rideId"
            }
            NotificationType.NEW_MESSAGE -> {
                val rideId = data["ride_id"] ?: ""
                "rideconnect://chat/$rideId"
            }
            NotificationType.SCHEDULED_RIDE_REMINDER -> {
                val rideId = data["ride_id"] ?: ""
                "rideconnect://scheduled-ride/$rideId"
            }
            NotificationType.PROMOTION -> {
                "rideconnect://promotions"
            }
            NotificationType.GENERAL -> {
                "rideconnect://home"
            }
        }
        
        return Intent(Intent.ACTION_VIEW, deepLink.toUri()).apply {
            flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TOP
            setPackage(context.packageName)
        }
    }
    
    /**
     * Process notification data and extract relevant information.
     */
    fun processNotificationData(data: Map<String, String>): NotificationData {
        val type = data["type"]?.let { typeString ->
            try {
                NotificationType.valueOf(typeString.uppercase())
            } catch (e: IllegalArgumentException) {
                NotificationType.GENERAL
            }
        } ?: NotificationType.GENERAL
        
        return NotificationData(
            type = type,
            title = data["title"] ?: "RideConnect",
            body = data["body"] ?: "",
            rideId = data["ride_id"],
            userId = data["user_id"],
            additionalData = data
        )
    }
}

/**
 * Processed notification data.
 */
data class NotificationData(
    val type: NotificationType,
    val title: String,
    val body: String,
    val rideId: String? = null,
    val userId: String? = null,
    val additionalData: Map<String, String> = emptyMap()
)

/**
 * Manager for notification preferences.
 * Requirements: 19.7, 27.2
 */
@Singleton
class NotificationPreferences @Inject constructor(
    @ApplicationContext private val context: Context
) {
    private val prefs = context.getSharedPreferences("notification_prefs", Context.MODE_PRIVATE)
    
    /**
     * Check if notification type is enabled.
     * Requirements: 19.7
     */
    fun isNotificationEnabled(type: NotificationType): Boolean {
        return prefs.getBoolean(type.name, true) // Default to enabled
    }
    
    /**
     * Enable or disable notification type.
     * Requirements: 19.7, 27.2
     */
    fun setNotificationEnabled(type: NotificationType, enabled: Boolean) {
        prefs.edit().putBoolean(type.name, enabled).apply()
    }
    
    /**
     * Get all notification preferences.
     */
    fun getAllPreferences(): Map<NotificationType, Boolean> {
        return NotificationType.values().associateWith { type ->
            isNotificationEnabled(type)
        }
    }
    
    /**
     * Reset all preferences to default (enabled).
     */
    fun resetToDefaults() {
        prefs.edit().clear().apply()
    }
}
