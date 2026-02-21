package com.rideconnect.core.common.util

import kotlinx.coroutines.delay
import kotlin.math.pow

/**
 * Retry configuration for exponential backoff
 */
data class RetryConfig(
    val maxAttempts: Int = 3,
    val initialDelayMs: Long = 1000L,
    val maxDelayMs: Long = 30000L,
    val factor: Double = 2.0
)

/**
 * Executes a suspending block with exponential backoff retry logic.
 * 
 * @param config Retry configuration with max attempts and delay parameters
 * @param block The suspending function to execute with retry
 * @return Result of the block execution
 * @throws Exception The last exception if all retry attempts fail
 * 
 * Example usage:
 * ```
 * val result = retryWithExponentialBackoff(
 *     config = RetryConfig(maxAttempts = 3, initialDelayMs = 1000L)
 * ) {
 *     apiService.fetchData()
 * }
 * ```
 */
suspend fun <T> retryWithExponentialBackoff(
    config: RetryConfig = RetryConfig(),
    block: suspend () -> T
): T {
    var currentAttempt = 0
    var lastException: Exception? = null
    
    while (currentAttempt < config.maxAttempts) {
        try {
            return block()
        } catch (e: Exception) {
            lastException = e
            currentAttempt++
            
            if (currentAttempt >= config.maxAttempts) {
                throw e
            }
            
            // Calculate delay with exponential backoff
            val delayMs = calculateDelay(
                attempt = currentAttempt,
                initialDelay = config.initialDelayMs,
                factor = config.factor,
                maxDelay = config.maxDelayMs
            )
            
            delay(delayMs)
        }
    }
    
    // This should never be reached, but throw the last exception if it somehow does
    throw lastException ?: IllegalStateException("Retry failed without exception")
}

/**
 * Calculates the delay for the current retry attempt using exponential backoff.
 * 
 * Formula: min(initialDelay * (factor ^ (attempt - 1)), maxDelay)
 * 
 * @param attempt Current attempt number (1-based)
 * @param initialDelay Initial delay in milliseconds
 * @param factor Exponential factor (typically 2.0)
 * @param maxDelay Maximum delay cap in milliseconds
 * @return Calculated delay in milliseconds
 */
private fun calculateDelay(
    attempt: Int,
    initialDelay: Long,
    factor: Double,
    maxDelay: Long
): Long {
    val exponentialDelay = (initialDelay * factor.pow(attempt - 1)).toLong()
    return minOf(exponentialDelay, maxDelay)
}

/**
 * Executes a suspending block with exponential backoff retry logic,
 * only retrying on specific exception types.
 * 
 * @param config Retry configuration
 * @param retryOn List of exception classes to retry on
 * @param block The suspending function to execute with retry
 * @return Result of the block execution
 * @throws Exception The last exception if all retry attempts fail or if exception is not retryable
 */
suspend fun <T> retryWithExponentialBackoffOn(
    config: RetryConfig = RetryConfig(),
    retryOn: List<Class<out Exception>>,
    block: suspend () -> T
): T {
    var currentAttempt = 0
    var lastException: Exception? = null
    
    while (currentAttempt < config.maxAttempts) {
        try {
            return block()
        } catch (e: Exception) {
            // Check if this exception type should be retried
            val shouldRetry = retryOn.any { it.isInstance(e) }
            
            if (!shouldRetry) {
                throw e
            }
            
            lastException = e
            currentAttempt++
            
            if (currentAttempt >= config.maxAttempts) {
                throw e
            }
            
            val delayMs = calculateDelay(
                attempt = currentAttempt,
                initialDelay = config.initialDelayMs,
                factor = config.factor,
                maxDelay = config.maxDelayMs
            )
            
            delay(delayMs)
        }
    }
    
    throw lastException ?: IllegalStateException("Retry failed without exception")
}
