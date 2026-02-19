package com.rideconnect.core.data.worker

import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.content.Context
import android.content.Intent
import android.os.Build
import androidx.core.app.NotificationCompat
import androidx.hilt.work.HiltWorker
import androidx.work.CoroutineWorker
import androidx.work.WorkerParameters
import com.rideconnect.core.domain.repository.ScheduledRideRepository
import dagger.assisted.Assisted
import dagger.assisted.AssistedInject

/**
 * Worker for sending scheduled ride reminders 30 minutes before ride time.
 * 
 * Requirements: 4.5
 */
@HiltWorker
class ScheduledRideReminderWorker @AssistedInject constructor(
    @Assisted private val context: Context,
    @Assisted workerParams: WorkerParameters,
    private val scheduledRideRepository: ScheduledRideRepository
) : CoroutineWorker(context, workerParams) {

    companion object {
        const val RIDE_ID_KEY = "ride_id"
        const val PICKUP_ADDRESS_KEY = "pickup_address"
        const val SCHEDULED_TIME_KEY = "scheduled_time"
        
        private const val CHANNEL_ID = "scheduled_ride_reminders"
        private const val CHANNEL_NAME = "Scheduled Ride Reminders"
        private const val NOTIFICATION_ID_BASE = 2000
    }

    override suspend fun doWork(): Result {
        return try {
            val rideId = inputData.getString(RIDE_ID_KEY) ?: return Result.failure()
            val pickupAddress = inputData.getString(PICKUP_ADDRESS_KEY) ?: "your pickup location"
            val scheduledTime = inputData.getLong(SCHEDULED_TIME_KEY, 0L)

            // Create notification channel (required for Android 8.0+)
            createNotificationChannel()

            // Send notification
            sendReminderNotification(rideId, pickupAddress, scheduledTime)

            Result.success()
        } catch (e: Exception) {
            e.printStackTrace()
            Result.failure()
        }
    }

    private fun createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                CHANNEL_ID,
                CHANNEL_NAME,
                NotificationManager.IMPORTANCE_HIGH
            ).apply {
                description = "Notifications for scheduled ride reminders"
                enableVibration(true)
                enableLights(true)
            }

            val notificationManager = context.getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
            notificationManager.createNotificationChannel(channel)
        }
    }

    private fun sendReminderNotification(rideId: String, pickupAddress: String, scheduledTime: Long) {
        val notificationManager = context.getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager

        // Create intent to open the app when notification is tapped
        val intent = context.packageManager.getLaunchIntentForPackage(context.packageName)?.apply {
            flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
            putExtra("ride_id", rideId)
            putExtra("notification_type", "scheduled_ride_reminder")
        }

        val pendingIntent = PendingIntent.getActivity(
            context,
            rideId.hashCode(),
            intent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )

        // Build notification
        val notification = NotificationCompat.Builder(context, CHANNEL_ID)
            .setSmallIcon(android.R.drawable.ic_dialog_info) // Replace with app icon
            .setContentTitle("Scheduled Ride Reminder")
            .setContentText("Your ride to $pickupAddress is in 30 minutes")
            .setStyle(
                NotificationCompat.BigTextStyle()
                    .bigText("Your scheduled ride to $pickupAddress is starting in 30 minutes. Please be ready at your pickup location.")
            )
            .setPriority(NotificationCompat.PRIORITY_HIGH)
            .setCategory(NotificationCompat.CATEGORY_REMINDER)
            .setAutoCancel(true)
            .setContentIntent(pendingIntent)
            .setVibrate(longArrayOf(0, 500, 200, 500))
            .build()

        // Use ride ID hash as notification ID to ensure uniqueness
        val notificationId = NOTIFICATION_ID_BASE + rideId.hashCode()
        notificationManager.notify(notificationId, notification)
    }
}
