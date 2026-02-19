package com.rideconnect.core.network.interceptor

import okhttp3.Interceptor
import okhttp3.Response
import timber.log.Timber
import java.io.IOException
import javax.inject.Inject

/**
 * Interceptor that handles HTTP error responses and converts them to appropriate exceptions.
 * Provides consistent error handling across all API calls.
 */
class ErrorInterceptor @Inject constructor() : Interceptor {
    
    override fun intercept(chain: Interceptor.Chain): Response {
        val request = chain.request()
        
        val response = try {
            chain.proceed(request)
        } catch (e: IOException) {
            Timber.e(e, "Network error for request: ${request.url}")
            throw NetworkException("Network error. Please check your connection.", e)
        }
        
        // Handle HTTP error status codes
        when (response.code) {
            in 200..299 -> {
                // Success - return response as is
                return response
            }
            400 -> {
                val errorBody = response.body?.string()
                Timber.w("Bad Request (400) for ${request.url}: $errorBody")
                throw BadRequestException(errorBody ?: "Invalid request")
            }
            401 -> {
                Timber.w("Unauthorized (401) for ${request.url}")
                throw UnauthorizedException("Authentication required. Please log in again.")
            }
            403 -> {
                Timber.w("Forbidden (403) for ${request.url}")
                throw ForbiddenException("Access denied")
            }
            404 -> {
                Timber.w("Not Found (404) for ${request.url}")
                throw NotFoundException("Resource not found")
            }
            408 -> {
                Timber.w("Request Timeout (408) for ${request.url}")
                throw TimeoutException("Request timed out. Please try again.")
            }
            429 -> {
                Timber.w("Too Many Requests (429) for ${request.url}")
                throw TooManyRequestsException("Too many requests. Please wait and try again.")
            }
            in 500..599 -> {
                Timber.e("Server Error (${response.code}) for ${request.url}")
                throw ServerException("Server error. Please try again later.")
            }
            else -> {
                Timber.e("Unexpected HTTP code (${response.code}) for ${request.url}")
                throw HttpException(response.code, "Unexpected error occurred")
            }
        }
    }
}

// Custom exception classes for different HTTP error scenarios
sealed class ApiException(message: String, cause: Throwable? = null) : IOException(message, cause)

class NetworkException(message: String, cause: Throwable? = null) : ApiException(message, cause)
class BadRequestException(message: String) : ApiException(message)
class UnauthorizedException(message: String) : ApiException(message)
class ForbiddenException(message: String) : ApiException(message)
class NotFoundException(message: String) : ApiException(message)
class TimeoutException(message: String) : ApiException(message)
class TooManyRequestsException(message: String) : ApiException(message)
class ServerException(message: String) : ApiException(message)
class HttpException(val code: Int, message: String) : ApiException(message)
