package com.rideconnect.core.data.location

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.app.Service
import android.content.Context
import android.content.Intent
import android.os.Build
import android.os.IBinder
import androidx.core.app.NotificationCompat
import com.rideconnect.core.domain.location.LocationRepository
import com.rideconnect.core.domain.location.LocationService
import com.rideconnect.core.domain.model.Location
import dagger.hilt.android.AndroidEntryPoint
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.cancel
import kotlinx.coroutines.flow.catch
import kotlinx.coroutines.launch
import javax.inject.Inject

/**
 * Foreground service for continuous location tracking in the background.
 * Used by Driver App to send location updates to backend every 10 seconds while online.
 * 
 * Requirements: 11.1, 11.2, 11.3, 29.5
 */
@AndroidEntryPoint
class LocationForegroundService : Service() {
    
    @Inject
    lateinit var locationService: LocationService
    
    @Inject
    lateinit var locationRepository: LocationRepository
    
    private val serviceScope = CoroutineScope(Dispatchers.Default + Job())
    private var locationJob: Job? = null
    
    companion object {
        private const val NOTIFICATION_ID = 1001
        private const val CHANNEL_ID = "location_tracking_channel"
        private const val CHANNEL_NAME = "Location Tracking"
        private const val LOCATION_UPDATE_INTERVAL_MS = 10_000L // 10 seconds
        
        fun startService(context: Context) {
            val intent = Intent(context, LocationForegroundService::class.java)
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                context.startForegroundService(intent)
            } else {
                context.startService(intent)
            }
        }
        
        fun stopService(context: Context) {
            val intent = Intent(context, LocationForegroundService::class.java)
            context.stopService(intent)
        }
    }
    
    override fun onCreate() {
        super.onCreate()
        createNotificationChannel()
    }
    
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        startForeground(NOTIFICATION_ID, createNotification())
        startLocationTracking()
        return START_STICKY
    }
    
    override fun onBind(intent: Intent?): IBinder? = null
    
    override fun onDestroy() {
        stopLocationTracking()
        serviceScope.cancel()
        super.onDestroy()
    }
    
    private fun startLocationTracking() {
        if (locationJob?.isActive == true) {
            return
        }
        
        try {
            locationService.startLocationUpdates(LOCATION_UPDATE_INTERVAL_MS)
            
            locationJob = serviceScope.launch {
                locationService.locationFlow
                    .catch { e ->
                        // Log error but continue tracking
                        android.util.Log.e("LocationService", "Location update error", e)
                    }
                    .collect { location ->
                        sendLocationToBackend(location)
                    }
            }
        } catch (e: SecurityException) {
            // Permission not granted, stop service
            stopSelf()
        }
    }
    
    private fun stopLocationTracking() {
        locationJob?.cancel()
        locationJob = null
        locationService.stopLocationUpdates()
    }
    
    private suspend fun sendLocationToBackend(location: Location) {
        try {
            locationRepository.updateLocation(location)
        } catch (e: Exception) {
            // Log error but continue tracking
            android.util.Log.e("LocationService", "Failed to send location to backend", e)
        }
    }
    
    private fun createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                CHANNEL_ID,
                CHANNEL_NAME,
                NotificationManager.IMPORTANCE_LOW
            ).apply {
                description = "Tracks your location while you're online to match you with nearby rides"
                setShowBadge(false)
            }
            
            val notificationManager = getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
            notificationManager.createNotificationChannel(channel)
        }
    }
    
    private fun createNotification(): Notification {
        // Create intent to open the app when notification is tapped
        val pendingIntent = packageManager.getLaunchIntentForPackage(packageName)?.let { intent ->
            PendingIntent.getActivity(
                this,
                0,
                intent,
                PendingIntent.FLAG_IMMUTABLE or PendingIntent.FLAG_UPDATE_CURRENT
            )
        }
        
        return NotificationCompat.Builder(this, CHANNEL_ID)
            .setContentTitle("You're online")
            .setContentText("Tracking your location to match you with nearby rides")
            .setSmallIcon(android.R.drawable.ic_menu_mylocation)
            .setOngoing(true)
            .setContentIntent(pendingIntent)
            .setPriority(NotificationCompat.PRIORITY_LOW)
            .setCategory(NotificationCompat.CATEGORY_SERVICE)
            .build()
    }
}
