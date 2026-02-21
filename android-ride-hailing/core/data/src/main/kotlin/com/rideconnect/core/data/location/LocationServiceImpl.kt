package com.rideconnect.core.data.location

import android.Manifest
import android.content.Context
import android.content.pm.PackageManager
import android.location.LocationManager
import android.os.Looper
import androidx.core.content.ContextCompat
import com.google.android.gms.location.*
import com.rideconnect.core.domain.location.LocationService
import com.rideconnect.core.domain.model.Location
import dagger.hilt.android.qualifiers.ApplicationContext
import kotlinx.coroutines.channels.awaitClose
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.callbackFlow
import kotlinx.coroutines.tasks.await
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class LocationServiceImpl @Inject constructor(
    @ApplicationContext private val context: Context
) : LocationService {
    
    private val fusedLocationClient: FusedLocationProviderClient =
        LocationServices.getFusedLocationProviderClient(context)
    
    private val _locationFlow = MutableStateFlow<Location?>(null)
    
    private var locationCallback: LocationCallback? = null
    private var isUpdatesStarted = false
    private var currentPriority: Int = Priority.PRIORITY_BALANCED_POWER_ACCURACY
    private var isInBackground = false
    
    companion object {
        // Foreground update intervals
        const val FOREGROUND_INTERVAL_MS = 10_000L // 10 seconds
        const val FOREGROUND_FASTEST_INTERVAL_MS = 5_000L // 5 seconds
        
        // Background update intervals (battery optimization)
        const val BACKGROUND_INTERVAL_MS = 60_000L // 60 seconds
        const val BACKGROUND_FASTEST_INTERVAL_MS = 30_000L // 30 seconds
        
        // Emergency mode (SOS activated)
        const val EMERGENCY_INTERVAL_MS = 5_000L // 5 seconds
        const val EMERGENCY_FASTEST_INTERVAL_MS = 2_000L // 2 seconds
    }
    
    /**
     * Set background mode to reduce location update frequency
     * Requirements: 23.2, 23.6
     */
    fun setBackgroundMode(isBackground: Boolean) {
        if (this.isInBackground == isBackground) return
        
        this.isInBackground = isBackground
        
        // Restart location updates with new interval if already started
        if (isUpdatesStarted) {
            stopLocationUpdates()
            val interval = if (isBackground) BACKGROUND_INTERVAL_MS else FOREGROUND_INTERVAL_MS
            startLocationUpdates(interval)
        }
    }
    
    /**
     * Set high accuracy mode for emergency situations
     * Requirements: 9.6
     */
    fun setEmergencyMode(isEmergency: Boolean) {
        currentPriority = if (isEmergency) {
            Priority.PRIORITY_HIGH_ACCURACY
        } else {
            Priority.PRIORITY_BALANCED_POWER_ACCURACY
        }
        
        // Restart location updates with new priority if already started
        if (isUpdatesStarted) {
            stopLocationUpdates()
            val interval = if (isEmergency) EMERGENCY_INTERVAL_MS else FOREGROUND_INTERVAL_MS
            startLocationUpdates(interval)
        }
    }
    
    override fun startLocationUpdates(intervalMs: Long) {
        if (!hasLocationPermission()) {
            throw SecurityException("Location permission not granted")
        }
        
        if (isUpdatesStarted) {
            return
        }
        
        // Use battery-efficient settings
        // Requirements: 23.2, 29.3
        val actualInterval = if (isInBackground) {
            maxOf(intervalMs, BACKGROUND_INTERVAL_MS)
        } else {
            intervalMs
        }
        
        val fastestInterval = actualInterval / 2
        
        val locationRequest = LocationRequest.Builder(
            currentPriority,
            actualInterval
        ).apply {
            setMinUpdateIntervalMillis(fastestInterval)
            setMaxUpdateDelayMillis(actualInterval * 2)
            setWaitForAccurateLocation(false) // Don't wait for high accuracy to save battery
            setMinUpdateDistanceMeters(10f) // Only update if moved 10 meters
        }.build()
        
        locationCallback = object : LocationCallback() {
            override fun onLocationResult(result: LocationResult) {
                result.lastLocation?.let { androidLocation ->
                    val location = Location(
                        latitude = androidLocation.latitude,
                        longitude = androidLocation.longitude,
                        accuracy = androidLocation.accuracy,
                        timestamp = androidLocation.time
                    )
                    _locationFlow.value = location
                }
            }
        }
        
        try {
            fusedLocationClient.requestLocationUpdates(
                locationRequest,
                locationCallback!!,
                Looper.getMainLooper()
            )
            isUpdatesStarted = true
        } catch (e: SecurityException) {
            throw SecurityException("Location permission not granted", e)
        }
    }
    
    override fun stopLocationUpdates() {
        locationCallback?.let {
            fusedLocationClient.removeLocationUpdates(it)
            locationCallback = null
            isUpdatesStarted = false
        }
    }
    
    override val locationFlow: Flow<Location> = callbackFlow {
        _locationFlow.collect { location ->
            location?.let { trySend(it) }
        }
        awaitClose { stopLocationUpdates() }
    }
    
    override suspend fun getCurrentLocation(): Location? {
        if (!hasLocationPermission()) {
            return null
        }
        
        return try {
            val androidLocation = fusedLocationClient.lastLocation.await()
            androidLocation?.let {
                Location(
                    latitude = it.latitude,
                    longitude = it.longitude,
                    accuracy = it.accuracy,
                    timestamp = it.time
                )
            }
        } catch (e: SecurityException) {
            null
        } catch (e: Exception) {
            null
        }
    }
    
    override fun isLocationEnabled(): Boolean {
        val locationManager = context.getSystemService(Context.LOCATION_SERVICE) as LocationManager
        return locationManager.isProviderEnabled(LocationManager.GPS_PROVIDER) ||
                locationManager.isProviderEnabled(LocationManager.NETWORK_PROVIDER)
    }
    
    override fun hasLocationPermission(): Boolean {
        return ContextCompat.checkSelfPermission(
            context,
            Manifest.permission.ACCESS_FINE_LOCATION
        ) == PackageManager.PERMISSION_GRANTED ||
                ContextCompat.checkSelfPermission(
                    context,
                    Manifest.permission.ACCESS_COARSE_LOCATION
                ) == PackageManager.PERMISSION_GRANTED
    }
}
