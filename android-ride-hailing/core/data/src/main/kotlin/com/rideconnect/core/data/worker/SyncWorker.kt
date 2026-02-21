package com.rideconnect.core.data.worker

import android.content.Context
import androidx.hilt.work.HiltWorker
import androidx.work.CoroutineWorker
import androidx.work.WorkerParameters
import com.rideconnect.core.data.sync.SyncManager
import dagger.assisted.Assisted
import dagger.assisted.AssistedInject
import kotlinx.coroutines.delay

/**
 * Background worker for periodic data synchronization.
 * Syncs pending ratings, messages, profile updates, and other offline actions.
 */
@HiltWorker
class SyncWorker @AssistedInject constructor(
    @Assisted context: Context,
    @Assisted workerParams: WorkerParameters,
    private val syncManager: SyncManager
) : CoroutineWorker(context, workerParams) {
    
    override suspend fun doWork(): Result {
        return try {
            // Check if device is online
            if (!syncManager.isOnline.value) {
                // Retry later if offline
                return Result.retry()
            }
            
            // Attempt to sync pending actions
            var attempt = 0
            var success = false
            
            while (attempt < MAX_RETRY_ATTEMPTS && !success) {
                try {
                    syncManager.syncPendingActions()
                    
                    // Check if there are still pending actions
                    val pendingCount = syncManager.getPendingActionCount()
                    
                    if (pendingCount == 0) {
                        success = true
                    } else {
                        // Some actions failed, retry with exponential backoff
                        attempt++
                        if (attempt < MAX_RETRY_ATTEMPTS) {
                            val delayMs = calculateBackoffDelay(attempt)
                            delay(delayMs)
                        }
                    }
                } catch (e: Exception) {
                    attempt++
                    if (attempt < MAX_RETRY_ATTEMPTS) {
                        val delayMs = calculateBackoffDelay(attempt)
                        delay(delayMs)
                    }
                }
            }
            
            // Clean up completed actions
            syncManager.clearCompletedActions()
            
            if (success) {
                Result.success()
            } else {
                // Retry the work later
                Result.retry()
            }
        } catch (e: Exception) {
            // Retry on unexpected errors
            Result.retry()
        }
    }
    
    /**
     * Calculates exponential backoff delay
     * Attempt 1: 1 second
     * Attempt 2: 2 seconds
     * Attempt 3: 4 seconds
     */
    private fun calculateBackoffDelay(attempt: Int): Long {
        val baseDelay = 1000L // 1 second
        return baseDelay * (1 shl (attempt - 1)) // 2^(attempt-1) seconds
    }
    
    companion object {
        const val WORK_NAME = "sync_worker"
        private const val MAX_RETRY_ATTEMPTS = 3
    }
}
