package com.rideconnect.core.common.util

import android.os.SystemClock
import android.util.Log

/**
 * Utility for profiling app startup time.
 * Tracks initialization milestones and logs timing information.
 */
object StartupProfiler {
    private const val TAG = "StartupProfiler"
    private var appStartTime: Long = 0
    private val milestones = mutableMapOf<String, Long>()
    
    /**
     * Mark the start of app initialization
     */
    fun markAppStart() {
        appStartTime = SystemClock.elapsedRealtime()
        Log.d(TAG, "App start marked at $appStartTime")
    }
    
    /**
     * Record a milestone during startup
     */
    fun recordMilestone(name: String) {
        val currentTime = SystemClock.elapsedRealtime()
        val elapsed = currentTime - appStartTime
        milestones[name] = elapsed
        Log.d(TAG, "Milestone '$name' reached at ${elapsed}ms")
    }
    
    /**
     * Log all recorded milestones
     */
    fun logStartupMetrics() {
        val totalTime = SystemClock.elapsedRealtime() - appStartTime
        Log.i(TAG, "=== App Startup Metrics ===")
        Log.i(TAG, "Total startup time: ${totalTime}ms")
        
        milestones.entries.sortedBy { it.value }.forEach { (name, time) ->
            Log.i(TAG, "  $name: ${time}ms")
        }
        
        Log.i(TAG, "===========================")
    }
    
    /**
     * Get total startup time in milliseconds
     */
    fun getStartupTime(): Long {
        return SystemClock.elapsedRealtime() - appStartTime
    }
    
    /**
     * Check if startup time meets performance target (2 seconds)
     */
    fun meetsPerformanceTarget(): Boolean {
        return getStartupTime() <= 2000
    }
    
    /**
     * Reset profiler for new measurement
     */
    fun reset() {
        appStartTime = 0
        milestones.clear()
    }
}
