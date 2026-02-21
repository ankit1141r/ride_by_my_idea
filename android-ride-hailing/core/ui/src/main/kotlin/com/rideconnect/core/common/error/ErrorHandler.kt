package com.rideconnect.core.common.error

import android.content.Context
import retrofit2.HttpException
import java.io.IOException
import java.net.SocketTimeoutException
import java.net.UnknownHostException

/**
 * Central error handling utility for converting exceptions to user-friendly messages
 * Requirements: 26.1, 26.4
 */
object ErrorHandler {
    
    /**
     * Converts an exception to a user-friendly error message
     */
    fun getErrorMessage(context: Context, throwable: Throwable): String {
        return when (throwable) {
            is HttpException -> handleHttpException(context, throwable)
            is SocketTimeoutException -> "Request timed out. Please try again."
            is UnknownHostException -> "No internet connection. Please check your network."
            is IOException -> "Network error. Please check your connection."
            is LocationException -> handleLocationException(context, throwable)
            is PaymentException -> handlePaymentException(context, throwable)
            is ValidationException -> throwable.message ?: "Validation error. Please check your input."
            else -> "An error occurred. Please try again."
        }
    }
    
    /**
     * Handles HTTP exceptions based on status code
     */
    private fun handleHttpException(context: Context, exception: HttpException): String {
        return when (exception.code()) {
            400 -> "Invalid request. Please check your input."
            401 -> "Unauthorized. Please log in again."
            403 -> "Access forbidden. You don't have permission."
            404 -> "Resource not found."
            408 -> "Request timed out. Please try again."
            429 -> "Too many requests. Please wait and try again."
            500 -> "Server error. Please try again later."
            502, 503 -> "Service unavailable. Please try again later."
            else -> "An error occurred. Please try again."
        }
    }
    
    /**
     * Handles location-specific exceptions
     */
    private fun handleLocationException(context: Context, exception: LocationException): String {
        return when (exception.type) {
            LocationErrorType.PERMISSION_DENIED -> "Location permission denied. Please enable location access."
            LocationErrorType.SERVICES_DISABLED -> "Location services are disabled. Please enable GPS."
            LocationErrorType.ACCURACY_LOW -> "GPS signal is weak. Please move to an open area."
            LocationErrorType.TIMEOUT -> "Location request timed out. Please try again."
        }
    }
    
    /**
     * Handles payment-specific exceptions
     */
    private fun handlePaymentException(context: Context, exception: PaymentException): String {
        return when (exception.type) {
            PaymentErrorType.INSUFFICIENT_FUNDS -> "Insufficient funds. Please add money to your wallet."
            PaymentErrorType.CARD_DECLINED -> "Card declined. Please try a different payment method."
            PaymentErrorType.EXPIRED_CARD -> "Card expired. Please update your card details."
            PaymentErrorType.INVALID_CARD -> "Invalid card details. Please check and try again."
            PaymentErrorType.GATEWAY_ERROR -> "Payment gateway error. Please try again."
            PaymentErrorType.NETWORK_ERROR -> "Payment network error. Please check your connection."
        }
    }
    
    /**
     * Determines if an error is retryable
     */
    fun isRetryable(throwable: Throwable): Boolean {
        return when (throwable) {
            is SocketTimeoutException -> true
            is UnknownHostException -> true
            is IOException -> true
            is HttpException -> throwable.code() in listOf(408, 429, 500, 502, 503)
            else -> false
        }
    }
    
    /**
     * Gets suggested action for an error
     */
    fun getSuggestedAction(context: Context, throwable: Throwable): String? {
        return when (throwable) {
            is UnknownHostException -> "Please check your internet connection and try again."
            is LocationException -> when (throwable.type) {
                LocationErrorType.PERMISSION_DENIED -> "Go to Settings and enable location permission."
                LocationErrorType.SERVICES_DISABLED -> "Go to Settings and enable location services."
                LocationErrorType.ACCURACY_LOW -> "Move to an open area for better GPS signal."
                else -> null
            }
            is PaymentException -> when (throwable.type) {
                PaymentErrorType.INSUFFICIENT_FUNDS -> "Add money to your wallet to continue."
                PaymentErrorType.CARD_DECLINED -> "Try using a different payment method."
                PaymentErrorType.EXPIRED_CARD -> "Update your card details in Settings."
                else -> "Please contact support for assistance."
            }
            is HttpException -> when (throwable.code()) {
                401 -> "Please log in again to continue."
                429 -> "Please wait a moment and try again."
                else -> null
            }
            else -> null
        }
    }
}

/**
 * Custom exception for location-related errors
 */
class LocationException(
    val type: LocationErrorType,
    message: String? = null
) : Exception(message)

enum class LocationErrorType {
    PERMISSION_DENIED,
    SERVICES_DISABLED,
    ACCURACY_LOW,
    TIMEOUT
}

/**
 * Custom exception for payment-related errors
 */
class PaymentException(
    val type: PaymentErrorType,
    message: String? = null
) : Exception(message)

enum class PaymentErrorType {
    INSUFFICIENT_FUNDS,
    CARD_DECLINED,
    EXPIRED_CARD,
    INVALID_CARD,
    GATEWAY_ERROR,
    NETWORK_ERROR
}

/**
 * Custom exception for validation errors
 */
class ValidationException(message: String) : Exception(message)
