package com.rideconnect.core.data.worker

import android.content.Context
import androidx.work.*
import com.rideconnect.core.domain.model.ScheduledRide
import dagger.hilt.android.qualifiers.ApplicationContext
import java.util.concurrent.TimeUnit
import javax.inject.Inject
import javax.inject.Singleton

/**
 * Manager for scheduling and canceling ride reminder notifications.
 * 
 * Requirements: 4.5
 */
@Singleton
class ScheduledRideReminderManager @Inject constructor(
    @ApplicationContext private val context: Context
) {
    private val workManager = WorkManager.getInstance(context)

    companion object {
        private const val REMINDER_WORK_TAG_PREFIX = "scheduled_ride_reminder_"
        private const val REMINDER_ADVANCE_MINUTES = 30L
    }

    /**
     * Schedule a reminder notification for a scheduled ride.
     * The reminder will be sent 30 minutes before the scheduled time.
     * 
     * Requirements: 4.5
     */
    fun scheduleReminder(ride: ScheduledRide) {
        val currentTime = System.currentTimeMillis()
        val reminderTime = ride.scheduledTime - TimeUnit.MINUTES.toMillis(REMINDER_ADVANCE_MINUTES)
        
        // Only schedule if reminder time is in the future
        if (reminderTime <= currentTime) {
            return
        }

        val delay = reminderTime - currentTime

        val inputData = workDataOf(
            ScheduledRideReminderWorker.RIDE_ID_KEY to ride.id,
            ScheduledRideReminderWorker.PICKUP_ADDRESS_KEY to (ride.pickupLocation.address ?: "Unknown location"),
            ScheduledRideReminderWorker.SCHEDULED_TIME_KEY to ride.scheduledTime
        )

        val reminderWork = OneTimeWorkRequestBuilder<ScheduledRideReminderWorker>()
            .setInitialDelay(delay, TimeUnit.MILLISECONDS)
            .setInputData(inputData)
            .addTag(getReminderWorkTag(ride.id))
            .setConstraints(
                Constraints.Builder()
                    .setRequiresBatteryNotLow(false) // Allow even on low battery
                    .build()
            )
            .build()

        workManager.enqueueUniqueWork(
            getReminderWorkTag(ride.id),
            ExistingWorkPolicy.REPLACE,
            reminderWork
        )
    }

    /**
     * Cancel a scheduled reminder for a ride.
     * 
     * Requirements: 4.6
     */
    fun cancelReminder(rideId: String) {
        workManager.cancelAllWorkByTag(getReminderWorkTag(rideId))
    }

    /**
     * Cancel all scheduled reminders.
     */
    fun cancelAllReminders() {
        workManager.cancelAllWorkByTag(REMINDER_WORK_TAG_PREFIX)
    }

    private fun getReminderWorkTag(rideId: String): String {
        return "$REMINDER_WORK_TAG_PREFIX$rideId"
    }
}
