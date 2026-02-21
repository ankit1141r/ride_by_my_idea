package com.rideconnect.core.data.sync

import androidx.work.Constraints
import androidx.work.ExistingPeriodicWorkPolicy
import androidx.work.NetworkType
import androidx.work.PeriodicWorkRequestBuilder
import androidx.work.WorkManager
import com.rideconnect.core.data.worker.SyncWorker
import java.util.concurrent.TimeUnit
import javax.inject.Inject
import javax.inject.Singleton

/**
 * Schedules periodic background sync work
 */
@Singleton
class SyncScheduler @Inject constructor(
    private val workManager: WorkManager
) {
    
    /**
     * Schedules periodic sync work that runs every 15 minutes when network is available
     */
    fun scheduleSyncWork() {
        val constraints = Constraints.Builder()
            .setRequiredNetworkType(NetworkType.CONNECTED)
            .build()
        
        val syncWorkRequest = PeriodicWorkRequestBuilder<SyncWorker>(
            repeatInterval = 15,
            repeatIntervalTimeUnit = TimeUnit.MINUTES
        )
            .setConstraints(constraints)
            .build()
        
        workManager.enqueueUniquePeriodicWork(
            SyncWorker.WORK_NAME,
            ExistingPeriodicWorkPolicy.KEEP,
            syncWorkRequest
        )
    }
    
    /**
     * Cancels scheduled sync work
     */
    fun cancelSyncWork() {
        workManager.cancelUniqueWork(SyncWorker.WORK_NAME)
    }
}
