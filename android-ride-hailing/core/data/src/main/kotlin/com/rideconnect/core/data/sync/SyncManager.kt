package com.rideconnect.core.data.sync

import android.content.Context
import android.net.ConnectivityManager
import android.net.Network
import android.net.NetworkCapabilities
import android.net.NetworkRequest
import androidx.work.WorkManager
import com.rideconnect.core.database.dao.SyncActionDao
import com.rideconnect.core.database.entity.SyncActionEntity
import dagger.hilt.android.qualifiers.ApplicationContext
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock
import javax.inject.Inject
import javax.inject.Singleton

/**
 * Manages offline mode and data synchronization.
 * Tracks network connectivity, queues actions performed offline, and syncs when connection is restored.
 */
@Singleton
class SyncManager @Inject constructor(
    @ApplicationContext private val context: Context,
    private val syncActionDao: SyncActionDao,
    private val workManager: WorkManager
) {
    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.IO)
    private val connectivityManager = context.getSystemService(Context.CONNECTIVITY_SERVICE) as ConnectivityManager
    
    private val _isOnline = MutableStateFlow(false)
    val isOnline: StateFlow<Boolean> = _isOnline.asStateFlow()
    
    private val _isSyncing = MutableStateFlow(false)
    val isSyncing: StateFlow<Boolean> = _isSyncing.asStateFlow()
    
    private val syncMutex = Mutex()
    
    private val networkCallback = object : ConnectivityManager.NetworkCallback() {
        override fun onAvailable(network: Network) {
            _isOnline.value = true
            scope.launch {
                syncPendingActions()
            }
        }
        
        override fun onLost(network: Network) {
            _isOnline.value = false
        }
    }
    
    init {
        // Check initial connectivity state
        _isOnline.value = checkNetworkConnectivity()
        
        // Register network callback
        val networkRequest = NetworkRequest.Builder()
            .addCapability(NetworkCapabilities.NET_CAPABILITY_INTERNET)
            .addCapability(NetworkCapabilities.NET_CAPABILITY_VALIDATED)
            .build()
        
        connectivityManager.registerNetworkCallback(networkRequest, networkCallback)
    }
    
    /**
     * Checks if device has active network connectivity
     */
    private fun checkNetworkConnectivity(): Boolean {
        val network = connectivityManager.activeNetwork ?: return false
        val capabilities = connectivityManager.getNetworkCapabilities(network) ?: return false
        
        return capabilities.hasCapability(NetworkCapabilities.NET_CAPABILITY_INTERNET) &&
                capabilities.hasCapability(NetworkCapabilities.NET_CAPABILITY_VALIDATED)
    }
    
    /**
     * Queues an action to be performed when network is available
     */
    suspend fun queueAction(action: SyncAction) {
        syncActionDao.insertAction(
            SyncActionEntity(
                id = 0, // Auto-generated
                type = action.type.name,
                data = action.data,
                timestamp = System.currentTimeMillis(),
                retryCount = 0,
                status = SyncStatus.PENDING.name
            )
        )
    }
    
    /**
     * Syncs all pending actions with the backend
     */
    suspend fun syncPendingActions() {
        if (!_isOnline.value) return
        
        syncMutex.withLock {
            if (_isSyncing.value) return
            
            _isSyncing.value = true
            
            try {
                val pendingActions = syncActionDao.getPendingActions()
                
                for (actionEntity in pendingActions) {
                    try {
                        // Process the action based on type
                        val success = processSyncAction(actionEntity)
                        
                        if (success) {
                            // Mark as completed
                            syncActionDao.updateActionStatus(actionEntity.id, SyncStatus.COMPLETED.name)
                        } else {
                            // Increment retry count
                            val newRetryCount = actionEntity.retryCount + 1
                            
                            if (newRetryCount >= MAX_RETRY_ATTEMPTS) {
                                // Mark as failed after max retries
                                syncActionDao.updateActionStatus(actionEntity.id, SyncStatus.FAILED.name)
                            } else {
                                // Update retry count
                                syncActionDao.updateRetryCount(actionEntity.id, newRetryCount)
                            }
                        }
                    } catch (e: Exception) {
                        // Handle exception and update retry count
                        val newRetryCount = actionEntity.retryCount + 1
                        
                        if (newRetryCount >= MAX_RETRY_ATTEMPTS) {
                            syncActionDao.updateActionStatus(actionEntity.id, SyncStatus.FAILED.name)
                        } else {
                            syncActionDao.updateRetryCount(actionEntity.id, newRetryCount)
                        }
                    }
                }
            } finally {
                _isSyncing.value = false
            }
        }
    }
    
    /**
     * Processes a single sync action
     */
    private suspend fun processSyncAction(actionEntity: SyncActionEntity): Boolean {
        // This will be implemented by specific repositories
        // For now, return true to indicate success
        // Actual implementation will delegate to appropriate repository based on action type
        val actionType = try {
            SyncActionType.valueOf(actionEntity.type)
        } catch (e: IllegalArgumentException) {
            return false
        }
        
        return when (actionType) {
            SyncActionType.PROFILE_UPDATE -> {
                // Delegate to ProfileRepository
                true
            }
            SyncActionType.RATING_SUBMISSION -> {
                // Delegate to RatingRepository
                true
            }
            SyncActionType.CHAT_MESSAGE -> {
                // Delegate to ChatRepository
                true
            }
            SyncActionType.LOCATION_UPDATE -> {
                // Delegate to LocationRepository
                true
            }
            else -> false
        }
    }
    
    /**
     * Clears all completed sync actions from the database
     */
    suspend fun clearCompletedActions() {
        syncActionDao.deleteCompletedActions()
    }
    
    /**
     * Gets count of pending sync actions
     */
    suspend fun getPendingActionCount(): Int {
        return syncActionDao.getPendingActionCount()
    }
    
    /**
     * Unregisters network callback
     */
    fun cleanup() {
        connectivityManager.unregisterNetworkCallback(networkCallback)
    }
    
    companion object {
        private const val MAX_RETRY_ATTEMPTS = 3
    }
}

/**
 * Represents an action to be synced
 */
data class SyncAction(
    val type: SyncActionType,
    val data: String // JSON serialized data
)

/**
 * Types of actions that can be synced
 */
enum class SyncActionType {
    PROFILE_UPDATE,
    RATING_SUBMISSION,
    CHAT_MESSAGE,
    LOCATION_UPDATE,
    EMERGENCY_CONTACT_ADD,
    EMERGENCY_CONTACT_REMOVE
}

/**
 * Status of a sync action
 */
enum class SyncStatus {
    PENDING,
    IN_PROGRESS,
    COMPLETED,
    FAILED
}
