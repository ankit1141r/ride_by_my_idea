package com.rideconnect.core.common.util

import android.content.Context
import android.content.Intent
import android.content.IntentFilter
import android.os.BatteryManager
import android.os.PowerManager

/**
 * Utility for battery optimization and monitoring
 * Requirements: 11.6, 23.2, 23.6
 */
object BatteryOptimizationUtil {
    
    /**
     * Get current battery level as percentage (0-100)
     */
    fun getBatteryLevel(context: Context): Int {
        val batteryStatus: Intent? = IntentFilter(Intent.ACTION_BATTERY_CHANGED).let { filter ->
            context.registerReceiver(null, filter)
        }
        
        val level = batteryStatus?.getIntExtra(BatteryManager.EXTRA_LEVEL, -1) ?: -1
        val scale = batteryStatus?.getIntExtra(BatteryManager.EXTRA_SCALE, -1) ?: -1
        
        return if (level >= 0 && scale > 0) {
            (level * 100 / scale.toFloat()).toInt()
        } else {
            100 // Default to full if unable to determine
        }
    }
    
    /**
     * Check if battery is low (below 15%)
     * Requirements: 11.6
     */
    fun isBatteryLow(context: Context): Boolean {
        return getBatteryLevel(context) < 15
    }
    
    /**
     * Check if device is charging
     */
    fun isCharging(context: Context): Boolean {
        val batteryStatus: Intent? = IntentFilter(Intent.ACTION_BATTERY_CHANGED).let { filter ->
            context.registerReceiver(null, filter)
        }
        
        val status = batteryStatus?.getIntExtra(BatteryManager.EXTRA_STATUS, -1) ?: -1
        return status == BatteryManager.BATTERY_STATUS_CHARGING ||
                status == BatteryManager.BATTERY_STATUS_FULL
    }
    
    /**
     * Check if battery saver mode is enabled
     */
    fun isBatterySaverEnabled(context: Context): Boolean {
        val powerManager = context.getSystemService(Context.POWER_SERVICE) as? PowerManager
        return powerManager?.isPowerSaveMode == true
    }
    
    /**
     * Get recommended location update interval based on battery level
     * Requirements: 23.2, 23.6
     */
    fun getRecommendedLocationInterval(context: Context, isInBackground: Boolean): Long {
        val batteryLevel = getBatteryLevel(context)
        val isBatterySaver = isBatterySaverEnabled(context)
        
        return when {
            // Emergency mode - always use 5 seconds
            // (handled separately in LocationServiceImpl)
            
            // Battery saver mode - reduce frequency significantly
            isBatterySaver -> if (isInBackground) 120_000L else 30_000L
            
            // Low battery (< 15%) - reduce frequency
            batteryLevel < 15 -> if (isInBackground) 90_000L else 20_000L
            
            // Medium battery (15-30%) - slightly reduce frequency
            batteryLevel < 30 -> if (isInBackground) 60_000L else 15_000L
            
            // Normal battery (> 30%) - standard frequency
            else -> if (isInBackground) 60_000L else 10_000L
        }
    }
    
    /**
     * Check if location tracking should be paused due to battery constraints
     * Requirements: 11.6
     */
    fun shouldPauseLocationTracking(context: Context): Boolean {
        val batteryLevel = getBatteryLevel(context)
        val isCharging = isCharging(context)
        
        // Don't pause if charging
        if (isCharging) return false
        
        // Pause if battery is critically low (< 5%)
        return batteryLevel < 5
    }
    
    /**
     * Get battery optimization recommendation message
     */
    fun getBatteryOptimizationMessage(context: Context): String? {
        val batteryLevel = getBatteryLevel(context)
        val isBatterySaver = isBatterySaverEnabled(context)
        
        return when {
            batteryLevel < 5 -> "Battery critically low. Location tracking paused."
            batteryLevel < 15 -> "Battery low (${batteryLevel}%). Consider going offline to save battery."
            isBatterySaver -> "Battery saver mode enabled. Location updates reduced."
            else -> null
        }
    }
}
