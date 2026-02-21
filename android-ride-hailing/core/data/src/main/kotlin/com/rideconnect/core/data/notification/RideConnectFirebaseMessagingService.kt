package com.rideconnect.core.data.notification

import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.content.Context
import android.content.Intent
import android.os.Build
import androidx.core.app.NotificationCompat
import com.google.firebase.messaging.FirebaseMessagingService
import com.google.firebase.messaging.RemoteMessage

/**
 * Firebase Cloud Messaging service for handling push notifications.
 * Requirements: 19.1, 19.2
 */
class RideConnectFirebaseMessagingService : FirebaseMessagingService() {
    
    private val notificationManager: NotificationManager by lazy {
        getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
    }
    
    override fun onNewToken(token: String) {
        super.onNewToken(token)
        // Send token to backend
        // This will be handled by NotificationManager
    }
    
    override fun onMessageReceived(message: RemoteMessage) {
        super.onMessageReceived(message)
        
        // Handle notification payload
        message.notification?.let { notification ->
            val title = notification.title ?: "RideConnect"
            val body = notification.body ?: ""
            
            // Get notification type from data payload
            val notificationType = message.data["type"] ?: "general"
            val channelId = getChannelIdForType(notificationType)
            
            showNotification(
                title = title,
                body = body,
                channelId = channelId,
                data = message.data
            )
        }
        
        // Handle data-only messages
        if (message.data.isNotEmpty()) {
            handleDataMessage(message.data)
        }
    }
    
    private fun showNotification(
        title: String,
        body: String,
        channelId: String,
        data: Map<String, String>
    ) {
        // Create notification channel if needed
        createNotificationChannel(channelId)
        
        // Create intent for notification tap
        val intent = createIntentForNotification(data)
        val pendingIntent = PendingIntent.getActivity(
            this,
            0,
            intent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )
        
        // Build notification
        val notification = NotificationCompat.Builder(this, channelId)
            .setContentTitle(title)
            .setContentText(body)
            .setSmallIcon(android.R.drawable.ic_dialog_info) // TODO: Replace with app icon
            .setAutoCancel(true)
            .setContentIntent(pendingIntent)
            .setPriority(NotificationCompat.PRIORITY_HIGH)
            .build()
        
        // Show notification
        notificationManager.notify(System.currentTimeMillis().toInt(), notification)
    }
    
    private fun createNotificationChannel(channelId: String) {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = when (channelId) {
                CHANNEL_RIDE_UPDATES -> NotificationChannel(
                    channelId,
                    "Ride Updates",
                    NotificationManager.IMPORTANCE_HIGH
                ).apply {
                    description = "Notifications about ride status and updates"
                }
                CHANNEL_MESSAGES -> NotificationChannel(
                    channelId,
                    "Messages",
                    NotificationManager.IMPORTANCE_HIGH
                ).apply {
                    description = "Chat messages from riders/drivers"
                }
                CHANNEL_PROMOTIONS -> NotificationChannel(
                    channelId,
                    "Promotions",
                    NotificationManager.IMPORTANCE_LOW
                ).apply {
                    description = "Promotional offers and updates"
                }
                CHANNEL_GENERAL -> NotificationChannel(
                    channelId,
                    "General",
                    NotificationManager.IMPORTANCE_DEFAULT
                ).apply {
                    description = "General notifications"
                }
                else -> NotificationChannel(
                    CHANNEL_GENERAL,
                    "General",
                    NotificationManager.IMPORTANCE_DEFAULT
                )
            }
            
            notificationManager.createNotificationChannel(channel)
        }
    }
    
    private fun getChannelIdForType(type: String): String {
        return when (type) {
            "ride_request", "ride_accepted", "ride_started", "ride_completed", "ride_cancelled" -> CHANNEL_RIDE_UPDATES
            "new_message" -> CHANNEL_MESSAGES
            "promotion", "offer" -> CHANNEL_PROMOTIONS
            else -> CHANNEL_GENERAL
        }
    }
    
    private fun createIntentForNotification(data: Map<String, String>): Intent {
        // Create deep link intent based on notification type
        // This will be implemented based on app navigation structure
        return Intent(this, Class.forName("com.rideconnect.rider.MainActivity"))
            .apply {
                flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TOP
                putExtra("notification_type", data["type"])
                putExtra("notification_data", data.toString())
            }
    }
    
    private fun handleDataMessage(data: Map<String, String>) {
        // Handle data-only messages (silent notifications)
        // Can be used to update app state without showing notification
        val type = data["type"] ?: return
        
        when (type) {
            "location_update" -> {
                // Update driver location in real-time
            }
            "ride_status_update" -> {
                // Update ride status
            }
            else -> {
                // Handle other data messages
            }
        }
    }
    
    companion object {
        const val CHANNEL_RIDE_UPDATES = "ride_updates"
        const val CHANNEL_MESSAGES = "messages"
        const val CHANNEL_PROMOTIONS = "promotions"
        const val CHANNEL_GENERAL = "general"
    }
}
