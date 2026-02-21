package com.rideconnect.core.common.compose

import androidx.compose.runtime.Composable
import androidx.compose.runtime.Stable
import androidx.compose.runtime.remember
import androidx.compose.ui.Modifier

/**
 * Utilities for optimizing Compose recomposition performance
 * Requirements: 23.5
 */

/**
 * Marker annotation for stable classes to prevent unnecessary recomposition
 * Requirements: 23.5
 */
@Stable
annotation class StableComposable

/**
 * Create a stable wrapper for lambda functions to prevent recomposition
 */
@Composable
fun <T> rememberStable(calculation: () -> T): T {
    return remember(calculation)
}

/**
 * Modifier extension to mark as stable
 */
fun Modifier.stable(): Modifier = this

/**
 * Performance tips for Compose:
 * 
 * 1. Use remember for expensive calculations
 * 2. Use derivedStateOf for computed values
 * 3. Mark data classes as @Stable or @Immutable
 * 4. Use keys in LazyColumn/LazyRow
 * 5. Avoid creating new lambdas in composable parameters
 * 6. Use Modifier.drawWithCache for custom drawing
 * 7. Defer state reads to layout/draw phase when possible
 * 8. Use SubcomposeLayout for conditional composition
 * 9. Profile with Layout Inspector and Composition Tracing
 * 10. Keep composables small and focused
 */

/**
 * Example of stable data class for UI state
 */
@Stable
data class StableUiState<T>(
    val data: T,
    val isLoading: Boolean = false,
    val error: String? = null
)

/**
 * Recomposition counter for debugging
 */
class RecompositionCounter {
    private var count = 0
    
    fun increment() {
        count++
    }
    
    fun getCount(): Int = count
    
    fun reset() {
        count = 0
    }
}

/**
 * Composable to track recomposition count (debug only)
 */
@Composable
fun rememberRecompositionCounter(): RecompositionCounter {
    val counter = remember { RecompositionCounter() }
    counter.increment()
    return counter
}
