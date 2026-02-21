package com.rideconnect.core.data.notification

import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.content.Context
import android.content.Intent
import android.os.Build
import androidx.core.app.NotificationCompat
import com.google.firebase.messaging.FirebaseMessaging
import com.rideconnect.core.common.result.Result
import com.rideconnect.core.network.api.DriverApi
import dagger.hilt.android.qualifiers.ApplicationContext
import kotlinx.coroutines.tasks.await
import javax.inject.Inject
import javax.inject.Singleton

/**
 * Manager for handling push notifications and FCM token registration.
 * Requirements: 19.1, 19.2
 */
@Singleton
class NotificationManagerImpl @Inject constructor(
    @ApplicationContext private val context: Context,
    private val notificationManager: NotificationManager,
    private val driverApi: DriverApi,
    private val firebaseMessaging: FirebaseMessaging
) {
    
    /**
     * Register device token with backend.
     * Requirements: 19.1, 19.2
     */
    suspend fun registerDeviceToken(): Result<Unit> {
        return try {
            // Get FCM token
            val token = firebaseMessaging.token.await()
            
            // Send token to backend
            driverApi.registerDeviceToken(token)
            
            Result.Success(Unit)
        } catch (e: Exception) {
            Result.Error(e)
        }
    }
    
    /**
     * Show local notification.
     * Requirements: 19.3, 19.4, 19.5, 19.6
     */
    fun showLocalNotification(
        title: String,
        body: String,
        notificationType: NotificationType,
        data: Map<String, String> = emptyMap()
    ) {
        val channelId = notificationType.channelId
        
        // Create notification channel
        createNotificationChannel(channelId, notificationType)
        
        // Create intent for notification tap
        val intent = createIntentForNotification(notificationType, data)
        val pendingIntent = PendingIntent.getActivity(
            context,
            0,
            intent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )
        
        // Build notification
        val notification = NotificationCompat.Builder(context, channelId)
            .setContentTitle(title)
            .setContentText(body)
            .setSmallIcon(android.R.drawable.ic_dialog_info) // TODO: Replace with app icon
            .setAutoCancel(true)
            .setContentIntent(pendingIntent)
            .setPriority(notificationType.priority)
            .build()
        
        // Show notification
        notificationManager.notify(notificationType.notificationId, notification)
    }
    
    /**
     * Create notification channels for Android 8.0+.
     * Requirements: 19.3, 19.4, 19.5, 19.6
     */
    private fun createNotificationChannel(channelId: String, type: NotificationType) {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                channelId,
                type.channelName,
                type.importance
            ).apply {
                description = type.channelDescription
            }
            
            notificationManager.createNotificationChannel(channel)
        }
    }
    
    /**
     * Create intent for notification navigation.
     * Requirements: 19.8
     */
    private fun createIntentForNotification(
        type: NotificationType,
        data: Map<String, String>
    ): Intent {
        // Create deep link intent based on notification type
        // This will navigate to the appropriate screen when notification is tapped
        return Intent(context, Class.forName("com.rideconnect.rider.MainActivity"))
            .apply {
                flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TOP
                putExtra("notification_type", type.name)
                data.forEach { (key, value) ->
                    putExtra(key, value)
                }
            }
    }
    
    /**
     * Cancel a notification.
     */
    fun cancelNotification(notificationId: Int) {
        notificationManager.cancel(notificationId)
    }
    
    /**
     * Cancel all notifications.
     */
    fun cancelAllNotifications() {
        notificationManager.cancelAll()
    }
}

/**
 * Notification types with their configurations.
 * Requirements: 19.3, 19.4, 19.5, 19.6
 */
enum class NotificationType(
    val channelId: String,
    val channelName: String,
    val channelDescription: String,
    val importance: Int,
    val priority: Int,
    val notificationId: Int
) {
    RIDE_REQUEST(
        channelId = "ride_requests",
        channelName = "Ride Requests",
        channelDescription = "Notifications for new ride requests",
        importance = NotificationManager.IMPORTANCE_HIGH,
        priority = NotificationCompat.PRIORITY_HIGH,
        notificationId = 1001
    ),
    RIDE_ACCEPTED(
        channelId = "ride_updates",
        channelName = "Ride Updates",
        channelDescription = "Notifications about ride status updates",
        importance = NotificationManager.IMPORTANCE_HIGH,
        priority = NotificationCompat.PRIORITY_HIGH,
        notificationId = 1002
    ),
    RIDE_STARTED(
        channelId = "ride_updates",
        channelName = "Ride Updates",
        channelDescription = "Notifications about ride status updates",
        importance = NotificationManager.IMPORTANCE_HIGH,
        priority = NotificationCompat.PRIORITY_HIGH,
        notificationId = 1003
    ),
    RIDE_COMPLETED(
        channelId = "ride_updates",
        channelName = "Ride Updates",
        channelDescription = "Notifications about ride status updates",
        importance = NotificationManager.IMPORTANCE_HIGH,
        priority = NotificationCompat.PRIORITY_HIGH,
        notificationId = 1004
    ),
    RIDE_CANCELLED(
        channelId = "ride_updates",
        channelName = "Ride Updates",
        channelDescription = "Notifications about ride status updates",
        importance = NotificationManager.IMPORTANCE_HIGH,
        priority = NotificationCompat.PRIORITY_HIGH,
        notificationId = 1005
    ),
    NEW_MESSAGE(
        channelId = "messages",
        channelName = "Messages",
        channelDescription = "Chat messages from riders/drivers",
        importance = NotificationManager.IMPORTANCE_HIGH,
        priority = NotificationCompat.PRIORITY_HIGH,
        notificationId = 2001
    ),
    SCHEDULED_RIDE_REMINDER(
        channelId = "reminders",
        channelName = "Reminders",
        channelDescription = "Reminders for scheduled rides",
        importance = NotificationManager.IMPORTANCE_HIGH,
        priority = NotificationCompat.PRIORITY_HIGH,
        notificationId = 3001
    ),
    PROMOTION(
        channelId = "promotions",
        channelName = "Promotions",
        channelDescription = "Promotional offers and updates",
        importance = NotificationManager.IMPORTANCE_LOW,
        priority = NotificationCompat.PRIORITY_LOW,
        notificationId = 4001
    ),
    GENERAL(
        channelId = "general",
        channelName = "General",
        channelDescription = "General notifications",
        importance = NotificationManager.IMPORTANCE_DEFAULT,
        priority = NotificationCompat.PRIORITY_DEFAULT,
        notificationId = 5001
    )
}
