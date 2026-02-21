package com.rideconnect.core.common.animation

import androidx.compose.animation.core.AnimationSpec
import androidx.compose.animation.core.Spring
import androidx.compose.animation.core.spring
import androidx.compose.animation.core.tween
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import kotlinx.coroutines.delay

/**
 * Utilities for optimizing animations to maintain 60 FPS
 * Requirements: 23.5
 */
object AnimationOptimizer {
    
    // Standard animation durations
    const val DURATION_SHORT = 150 // milliseconds
    const val DURATION_MEDIUM = 300 // milliseconds
    const val DURATION_LONG = 500 // milliseconds
    
    // Target frame rate
    const val TARGET_FPS = 60
    const val FRAME_TIME_MS = 1000 / TARGET_FPS // ~16.67ms per frame
    
    /**
     * Get optimized spring animation spec
     * Requirements: 23.5
     */
    fun <T> getSpringSpec(
        dampingRatio: Float = Spring.DampingRatioMediumBouncy,
        stiffness: Float = Spring.StiffnessMedium
    ): AnimationSpec<T> {
        return spring(
            dampingRatio = dampingRatio,
            stiffness = stiffness
        )
    }
    
    /**
     * Get optimized tween animation spec
     * Requirements: 23.5
     */
    fun <T> getTweenSpec(durationMillis: Int = DURATION_MEDIUM): AnimationSpec<T> {
        return tween(durationMillis = durationMillis)
    }
    
    /**
     * Get fast animation spec for quick transitions
     */
    fun <T> getFastSpec(): AnimationSpec<T> {
        return tween(durationMillis = DURATION_SHORT)
    }
    
    /**
     * Get smooth animation spec for map marker movements
     * Requirements: 6.3, 23.5
     */
    fun <T> getSmoothMapAnimationSpec(): AnimationSpec<T> {
        return spring(
            dampingRatio = Spring.DampingRatioNoBouncy,
            stiffness = Spring.StiffnessLow
        )
    }
    
    /**
     * Check if animation duration is within performance budget
     * Requirements: 23.5
     */
    fun isWithinPerformanceBudget(durationMs: Int, frameCount: Int): Boolean {
        val expectedFrameTime = durationMs.toFloat() / frameCount
        return expectedFrameTime >= FRAME_TIME_MS
    }
    
    /**
     * Calculate recommended frame count for animation duration
     */
    fun getRecommendedFrameCount(durationMs: Int): Int {
        return (durationMs / FRAME_TIME_MS).toInt()
    }
    
    /**
     * Check if animations should be reduced based on accessibility settings
     * Requirements: 23.5, 27.1
     */
    fun shouldReduceAnimations(context: android.content.Context): Boolean {
        val resolver = context.contentResolver
        return try {
            android.provider.Settings.Global.getFloat(
                resolver,
                android.provider.Settings.Global.ANIMATOR_DURATION_SCALE,
                1f
            ) == 0f
        } catch (e: Exception) {
            false
        }
    }
}

/**
 * Frame rate monitor for debugging animation performance
 * Requirements: 23.5
 */
class FrameRateMonitor {
    private var frameCount = 0
    private var startTime = 0L
    private var currentFps = 0f
    
    /**
     * Record a frame
     */
    fun recordFrame() {
        if (startTime == 0L) {
            startTime = System.currentTimeMillis()
        }
        
        frameCount++
        
        val elapsed = System.currentTimeMillis() - startTime
        if (elapsed >= 1000) {
            currentFps = frameCount * 1000f / elapsed
            frameCount = 0
            startTime = System.currentTimeMillis()
        }
    }
    
    /**
     * Get current FPS
     */
    fun getCurrentFps(): Float = currentFps
    
    /**
     * Check if meeting 60 FPS target
     * Requirements: 23.5
     */
    fun isMeetingTarget(): Boolean = currentFps >= AnimationOptimizer.TARGET_FPS
    
    /**
     * Reset monitor
     */
    fun reset() {
        frameCount = 0
        startTime = 0L
        currentFps = 0f
    }
}

/**
 * Composable for monitoring frame rate during animations
 */
@Composable
fun rememberFrameRateMonitor(): FrameRateMonitor {
    return remember { FrameRateMonitor() }
}

/**
 * Composable effect to track animation performance
 */
@Composable
fun TrackAnimationPerformance(
    isAnimating: Boolean,
    onFpsUpdate: (Float) -> Unit
) {
    val monitor = rememberFrameRateMonitor()
    
    LaunchedEffect(isAnimating) {
        if (isAnimating) {
            while (true) {
                monitor.recordFrame()
                onFpsUpdate(monitor.getCurrentFps())
                delay(16) // ~60 FPS
            }
        } else {
            monitor.reset()
        }
    }
}
