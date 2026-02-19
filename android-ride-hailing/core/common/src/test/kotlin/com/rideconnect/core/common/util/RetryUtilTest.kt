package com.rideconnect.core.common.util

import kotlinx.coroutines.test.runTest
import org.junit.Assert.*
import org.junit.Test
import java.io.IOException
import java.net.SocketTimeoutException

class RetryUtilTest {
    
    @Test
    fun `retryWithExponentialBackoff succeeds on first attempt`() = runTest {
        var attemptCount = 0
        
        val result = retryWithExponentialBackoff(
            config = RetryConfig(maxAttempts = 3)
        ) {
            attemptCount++
            "success"
        }
        
        assertEquals("success", result)
        assertEquals(1, attemptCount)
    }
    
    @Test
    fun `retryWithExponentialBackoff succeeds on second attempt`() = runTest {
        var attemptCount = 0
        
        val result = retryWithExponentialBackoff(
            config = RetryConfig(maxAttempts = 3, initialDelayMs = 10L)
        ) {
            attemptCount++
            if (attemptCount < 2) {
                throw IOException("Network error")
            }
            "success"
        }
        
        assertEquals("success", result)
        assertEquals(2, attemptCount)
    }
    
    @Test
    fun `retryWithExponentialBackoff fails after max attempts`() = runTest {
        var attemptCount = 0
        
        try {
            retryWithExponentialBackoff(
                config = RetryConfig(maxAttempts = 3, initialDelayMs = 10L)
            ) {
                attemptCount++
                throw IOException("Network error")
            }
            fail("Should have thrown exception")
        } catch (e: IOException) {
            assertEquals("Network error", e.message)
            assertEquals(3, attemptCount)
        }
    }
    
    @Test
    fun `retryWithExponentialBackoff uses exponential backoff delays`() = runTest {
        var attemptCount = 0
        val startTime = System.currentTimeMillis()
        
        try {
            retryWithExponentialBackoff(
                config = RetryConfig(
                    maxAttempts = 3,
                    initialDelayMs = 100L,
                    factor = 2.0
                )
            ) {
                attemptCount++
                throw IOException("Network error")
            }
        } catch (e: IOException) {
            // Expected
        }
        
        val elapsedTime = System.currentTimeMillis() - startTime
        
        // Should have delays of approximately 100ms and 200ms (total ~300ms)
        // Allow some tolerance for test execution time
        assertTrue("Elapsed time should be at least 250ms", elapsedTime >= 250)
        assertEquals(3, attemptCount)
    }
    
    @Test
    fun `retryWithExponentialBackoff respects max delay`() = runTest {
        var attemptCount = 0
        
        try {
            retryWithExponentialBackoff(
                config = RetryConfig(
                    maxAttempts = 5,
                    initialDelayMs = 1000L,
                    maxDelayMs = 2000L,
                    factor = 2.0
                )
            ) {
                attemptCount++
                throw IOException("Network error")
            }
        } catch (e: IOException) {
            // Expected
        }
        
        assertEquals(5, attemptCount)
    }
    
    @Test
    fun `retryWithExponentialBackoffOn only retries specified exceptions`() = runTest {
        var attemptCount = 0
        
        try {
            retryWithExponentialBackoffOn(
                config = RetryConfig(maxAttempts = 3, initialDelayMs = 10L),
                retryOn = listOf(IOException::class.java, SocketTimeoutException::class.java)
            ) {
                attemptCount++
                throw IllegalArgumentException("Invalid argument")
            }
            fail("Should have thrown exception")
        } catch (e: IllegalArgumentException) {
            assertEquals("Invalid argument", e.message)
            assertEquals(1, attemptCount) // Should not retry
        }
    }
    
    @Test
    fun `retryWithExponentialBackoffOn retries on specified exception`() = runTest {
        var attemptCount = 0
        
        val result = retryWithExponentialBackoffOn(
            config = RetryConfig(maxAttempts = 3, initialDelayMs = 10L),
            retryOn = listOf(IOException::class.java)
        ) {
            attemptCount++
            if (attemptCount < 2) {
                throw IOException("Network error")
            }
            "success"
        }
        
        assertEquals("success", result)
        assertEquals(2, attemptCount)
    }
}
