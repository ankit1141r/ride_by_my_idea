package com.rideconnect.core.common.network

import com.rideconnect.core.common.result.Result
import com.rideconnect.core.common.result.error
import com.rideconnect.core.common.result.success
import com.rideconnect.core.common.util.RetryConfig
import com.rideconnect.core.common.util.retryWithExponentialBackoff
import retrofit2.Response
import java.io.IOException
import java.net.SocketTimeoutException
import java.net.UnknownHostException

/**
 * Executes a Retrofit API call with retry logic and converts the response to a Result.
 * 
 * This function automatically retries on network-related exceptions (IOException, 
 * SocketTimeoutException, UnknownHostException) using exponential backoff.
 * 
 * @param retryConfig Configuration for retry behavior
 * @param apiCall The suspending function that makes the API call
 * @return Result containing the response data or an error
 * 
 * Example usage:
 * ```
 * suspend fun getUser(userId: String): Result<User> = safeApiCall {
 *     api.getUser(userId)
 * }
 * ```
 */
suspend fun <T> safeApiCall(
    retryConfig: RetryConfig = RetryConfig(
        maxAttempts = 3,
        initialDelayMs = 1000L,
        maxDelayMs = 30000L,
        factor = 2.0
    ),
    apiCall: suspend () -> Response<T>
): Result<T> {
    return try {
        val response = retryWithExponentialBackoff(config = retryConfig) {
            try {
                apiCall()
            } catch (e: IOException) {
                throw e
            } catch (e: SocketTimeoutException) {
                throw e
            } catch (e: UnknownHostException) {
                throw e
            } catch (e: Exception) {
                // Don't retry on non-network exceptions
                throw NetworkException("API call failed", e)
            }
        }
        
        if (response.isSuccessful) {
            val body = response.body()
            if (body != null) {
                success(body)
            } else {
                error(NetworkException("Response body is null"))
            }
        } else {
            error(
                NetworkException(
                    "HTTP ${response.code()}: ${response.message()}",
                    null
                ),
                response.message()
            )
        }
    } catch (e: IOException) {
        error(NetworkException("Network error: ${e.message}", e), e.message)
    } catch (e: SocketTimeoutException) {
        error(NetworkException("Request timeout: ${e.message}", e), e.message)
    } catch (e: UnknownHostException) {
        error(NetworkException("No internet connection: ${e.message}", e), e.message)
    } catch (e: NetworkException) {
        error(e, e.message)
    } catch (e: Exception) {
        error(NetworkException("Unexpected error: ${e.message}", e), e.message)
    }
}

/**
 * Executes a Retrofit API call without retry logic and converts the response to a Result.
 * Use this for operations that should not be retried (e.g., POST requests that are not idempotent).
 * 
 * @param apiCall The suspending function that makes the API call
 * @return Result containing the response data or an error
 */
suspend fun <T> safeApiCallNoRetry(
    apiCall: suspend () -> Response<T>
): Result<T> {
    return try {
        val response = apiCall()
        
        if (response.isSuccessful) {
            val body = response.body()
            if (body != null) {
                success(body)
            } else {
                error(NetworkException("Response body is null"))
            }
        } else {
            error(
                NetworkException(
                    "HTTP ${response.code()}: ${response.message()}",
                    null
                ),
                response.message()
            )
        }
    } catch (e: IOException) {
        error(NetworkException("Network error: ${e.message}", e), e.message)
    } catch (e: SocketTimeoutException) {
        error(NetworkException("Request timeout: ${e.message}", e), e.message)
    } catch (e: UnknownHostException) {
        error(NetworkException("No internet connection: ${e.message}", e), e.message)
    } catch (e: Exception) {
        error(NetworkException("Unexpected error: ${e.message}", e), e.message)
    }
}

/**
 * Custom exception for network-related errors
 */
class NetworkException(
    message: String,
    cause: Throwable? = null
) : Exception(message, cause)
