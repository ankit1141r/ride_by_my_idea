package com.rideconnect.core.common.animation

import androidx.compose.animation.*
import androidx.compose.animation.core.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.platform.LocalContext
import com.rideconnect.core.common.animation.AnimationOptimizer

/**
 * Standardized transition animations following Material Design 3 motion guidelines.
 * 
 * Provides consistent animation durations, easing curves, and transition effects
 * throughout the application.
 */
object TransitionAnimations {
    
    // Standard durations (Material Design 3)
    const val DURATION_SHORT = 150
    const val DURATION_MEDIUM = 300
    const val DURATION_LONG = 500
    
    // Easing curves
    val EasingStandard = CubicBezierEasing(0.4f, 0.0f, 0.2f, 1.0f)
    val EasingDecelerate = CubicBezierEasing(0.0f, 0.0f, 0.2f, 1.0f)
    val EasingAccelerate = CubicBezierEasing(0.4f, 0.0f, 1.0f, 1.0f)
    val EasingEmphasized = CubicBezierEasing(0.2f, 0.0f, 0.0f, 1.0f)
    
    /**
     * Standard fade transition for screen changes.
     */
    @Composable
    fun fadeTransition(): EnterTransition {
        return fadeIn(
            animationSpec = tween(
                durationMillis = DURATION_MEDIUM,
                easing = EasingStandard
            )
        )
    }
    
    @Composable
    fun fadeExitTransition(): ExitTransition {
        return fadeOut(
            animationSpec = tween(
                durationMillis = DURATION_MEDIUM,
                easing = EasingStandard
            )
        )
    }
    
    /**
     * Slide transition for hierarchical navigation (forward).
     */
    @Composable
    fun slideInForward(): EnterTransition {
        return slideInHorizontally(
            initialOffsetX = { fullWidth -> fullWidth },
            animationSpec = tween(
                durationMillis = DURATION_MEDIUM,
                easing = EasingEmphasized
            )
        ) + fadeIn(
            animationSpec = tween(
                durationMillis = DURATION_MEDIUM,
                easing = EasingStandard
            )
        )
    }
    
    @Composable
    fun slideOutForward(): ExitTransition {
        return slideOutHorizontally(
            targetOffsetX = { fullWidth -> -fullWidth / 3 },
            animationSpec = tween(
                durationMillis = DURATION_MEDIUM,
                easing = EasingEmphasized
            )
        ) + fadeOut(
            animationSpec = tween(
                durationMillis = DURATION_MEDIUM,
                easing = EasingStandard
            )
        )
    }
    
    /**
     * Slide transition for hierarchical navigation (backward).
     */
    @Composable
    fun slideInBackward(): EnterTransition {
        return slideInHorizontally(
            initialOffsetX = { fullWidth -> -fullWidth / 3 },
            animationSpec = tween(
                durationMillis = DURATION_MEDIUM,
                easing = EasingEmphasized
            )
        ) + fadeIn(
            animationSpec = tween(
                durationMillis = DURATION_MEDIUM,
                easing = EasingStandard
            )
        )
    }
    
    @Composable
    fun slideOutBackward(): ExitTransition {
        return slideOutHorizontally(
            targetOffsetX = { fullWidth -> fullWidth },
            animationSpec = tween(
                durationMillis = DURATION_MEDIUM,
                easing = EasingEmphasized
            )
        ) + fadeOut(
            animationSpec = tween(
                durationMillis = DURATION_MEDIUM,
                easing = EasingStandard
            )
        )
    }
    
    /**
     * Scale transition for modal dialogs.
     */
    @Composable
    fun scaleInTransition(): EnterTransition {
        return scaleIn(
            initialScale = 0.8f,
            animationSpec = tween(
                durationMillis = DURATION_MEDIUM,
                easing = EasingEmphasized
            )
        ) + fadeIn(
            animationSpec = tween(
                durationMillis = DURATION_SHORT,
                easing = EasingStandard
            )
        )
    }
    
    @Composable
    fun scaleOutTransition(): ExitTransition {
        return scaleOut(
            targetScale = 0.8f,
            animationSpec = tween(
                durationMillis = DURATION_SHORT,
                easing = EasingAccelerate
            )
        ) + fadeOut(
            animationSpec = tween(
                durationMillis = DURATION_SHORT,
                easing = EasingStandard
            )
        )
    }
    
    /**
     * Expand/collapse transition for expandable content.
     */
    @Composable
    fun expandVertically(): EnterTransition {
        return expandVertically(
            animationSpec = tween(
                durationMillis = DURATION_MEDIUM,
                easing = EasingEmphasized
            )
        ) + fadeIn(
            animationSpec = tween(
                durationMillis = DURATION_MEDIUM,
                easing = EasingStandard
            )
        )
    }
    
    @Composable
    fun shrinkVertically(): ExitTransition {
        return shrinkVertically(
            animationSpec = tween(
                durationMillis = DURATION_MEDIUM,
                easing = EasingEmphasized
            )
        ) + fadeOut(
            animationSpec = tween(
                durationMillis = DURATION_MEDIUM,
                easing = EasingStandard
            )
        )
    }
    
    /**
     * Slide up transition for bottom sheets.
     */
    @Composable
    fun slideUpTransition(): EnterTransition {
        return slideInVertically(
            initialOffsetY = { fullHeight -> fullHeight },
            animationSpec = tween(
                durationMillis = DURATION_MEDIUM,
                easing = EasingEmphasized
            )
        ) + fadeIn(
            animationSpec = tween(
                durationMillis = DURATION_SHORT,
                easing = EasingStandard
            )
        )
    }
    
    @Composable
    fun slideDownTransition(): ExitTransition {
        return slideOutVertically(
            targetOffsetY = { fullHeight -> fullHeight },
            animationSpec = tween(
                durationMillis = DURATION_MEDIUM,
                easing = EasingAccelerate
            )
        ) + fadeOut(
            animationSpec = tween(
                durationMillis = DURATION_SHORT,
                easing = EasingStandard
            )
        )
    }
    
    /**
     * Checks if reduced motion is preferred (accessibility).
     */
    @Composable
    fun isReducedMotionPreferred(): Boolean {
        val context = LocalContext.current
        return AnimationOptimizer.shouldReduceAnimations(context)
    }
    
    /**
     * Gets appropriate transition based on reduced motion preference.
     */
    @Composable
    fun getEnterTransition(default: EnterTransition): EnterTransition {
        return if (isReducedMotionPreferred()) {
            fadeTransition()
        } else {
            default
        }
    }
    
    @Composable
    fun getExitTransition(default: ExitTransition): ExitTransition {
        return if (isReducedMotionPreferred()) {
            fadeExitTransition()
        } else {
            default
        }
    }
    
    /**
     * Spring animation spec for interactive elements.
     */
    fun <T> springSpec(
        dampingRatio: Float = Spring.DampingRatioMediumBouncy,
        stiffness: Float = Spring.StiffnessMedium
    ): SpringSpec<T> {
        return spring(
            dampingRatio = dampingRatio,
            stiffness = stiffness
        )
    }
    
    /**
     * Repeatable animation spec for loading indicators.
     */
    fun <T> repeatableSpec(
        iterations: Int = RepeatMode.Restart.ordinal,
        animation: DurationBasedAnimationSpec<T> = tween(DURATION_LONG)
    ): RepeatableSpec<T> {
        return repeatable(
            iterations = iterations,
            animation = animation,
            repeatMode = RepeatMode.Restart
        )
    }
    
    /**
     * Infinite repeatable animation for continuous animations.
     */
    fun <T> infiniteRepeatableSpec(
        animation: DurationBasedAnimationSpec<T> = tween(DURATION_LONG),
        repeatMode: RepeatMode = RepeatMode.Restart
    ): InfiniteRepeatableSpec<T> {
        return infiniteRepeatable(
            animation = animation,
            repeatMode = repeatMode
        )
    }
}
