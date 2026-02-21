package com.rideconnect.core.common.accessibility

import android.content.Context
import android.os.Build
import android.os.VibrationEffect
import android.os.Vibrator
import android.os.VibratorManager
import androidx.compose.foundation.clickable
import androidx.compose.foundation.interaction.MutableInteractionSource
import androidx.compose.foundation.layout.defaultMinSize
import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.unit.dp

/**
 * Accessibility utilities for ensuring WCAG 2.1 Level AA compliance
 * and supporting assistive technologies like TalkBack.
 */
object AccessibilityUtils {
    
    /**
     * Minimum touch target size as per Material Design and WCAG guidelines
     */
    val MIN_TOUCH_TARGET_SIZE = 48.dp
    
    /**
     * Provides haptic feedback for important actions
     */
    fun provideHapticFeedback(context: Context, duration: Long = 50) {
        val vibrator = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
            val vibratorManager = context.getSystemService(Context.VIBRATOR_MANAGER_SERVICE) as VibratorManager
            vibratorManager.defaultVibrator
        } else {
            @Suppress("DEPRECATION")
            context.getSystemService(Context.VIBRATOR_SERVICE) as Vibrator
        }
        
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            vibrator.vibrate(
                VibrationEffect.createOneShot(duration, VibrationEffect.DEFAULT_AMPLITUDE)
            )
        } else {
            @Suppress("DEPRECATION")
            vibrator.vibrate(duration)
        }
    }
    
    /**
     * Provides strong haptic feedback for critical actions (e.g., SOS button)
     */
    fun provideStrongHapticFeedback(context: Context) {
        val vibrator = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
            val vibratorManager = context.getSystemService(Context.VIBRATOR_MANAGER_SERVICE) as VibratorManager
            vibratorManager.defaultVibrator
        } else {
            @Suppress("DEPRECATION")
            context.getSystemService(Context.VIBRATOR_SERVICE) as Vibrator
        }
        
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            vibrator.vibrate(
                VibrationEffect.createWaveform(
                    longArrayOf(0, 100, 50, 100),
                    intArrayOf(0, 255, 0, 255),
                    -1
                )
            )
        } else {
            @Suppress("DEPRECATION")
            vibrator.vibrate(longArrayOf(0, 100, 50, 100), -1)
        }
    }
}

/**
 * Modifier extension to ensure minimum touch target size for accessibility
 */
fun Modifier.accessibleTouchTarget(): Modifier {
    return this.defaultMinSize(
        minWidth = AccessibilityUtils.MIN_TOUCH_TARGET_SIZE,
        minHeight = AccessibilityUtils.MIN_TOUCH_TARGET_SIZE
    )
}

/**
 * Modifier extension to add content description for screen readers
 */
fun Modifier.accessibleDescription(description: String): Modifier {
    return this.semantics {
        contentDescription = description
    }
}

/**
 * Composable modifier for clickable elements with accessibility support
 * Ensures minimum touch target size and provides haptic feedback
 */
@Composable
fun Modifier.accessibleClickable(
    contentDescription: String,
    enabled: Boolean = true,
    provideHapticFeedback: Boolean = false,
    onClick: () -> Unit
): Modifier {
    val context = LocalContext.current
    val interactionSource = remember { MutableInteractionSource() }
    
    return this
        .accessibleTouchTarget()
        .semantics {
            this.contentDescription = contentDescription
        }
        .clickable(
            enabled = enabled,
            interactionSource = interactionSource,
            indication = androidx.compose.material.ripple.rememberRipple()
        ) {
            if (provideHapticFeedback) {
                AccessibilityUtils.provideHapticFeedback(context)
            }
            onClick()
        }
}
