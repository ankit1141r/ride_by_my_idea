package com.rideconnect.core.common.security

import timber.log.Timber

/**
 * Input validation utilities to prevent injection attacks
 * Requirements: 24.3
 */
object InputValidator {
    
    // Regex patterns for validation
    private val SQL_INJECTION_PATTERN = Regex(
        pattern = "('|(\\-\\-)|(;)|(\\|\\|)|(\\*))",
        option = RegexOption.IGNORE_CASE
    )
    
    private val XSS_PATTERN = Regex(
        pattern = "(<script|<iframe|javascript:|onerror=|onload=)",
        option = RegexOption.IGNORE_CASE
    )
    
    private val PHONE_NUMBER_PATTERN = Regex("^\\+?[1-9]\\d{1,14}$")
    
    private val EMAIL_PATTERN = Regex(
        "^[A-Za-z0-9+_.-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$"
    )
    
    private val ALPHANUMERIC_PATTERN = Regex("^[a-zA-Z0-9\\s]+$")
    
    /**
     * Validate and sanitize text input to prevent SQL injection
     * Requirements: 24.3
     */
    fun sanitizeSqlInput(input: String): String {
        if (containsSqlInjection(input)) {
            Timber.w("Potential SQL injection detected in input")
            // Remove dangerous characters
            return input.replace(SQL_INJECTION_PATTERN, "")
        }
        return input
    }
    
    /**
     * Check if input contains potential SQL injection patterns
     */
    fun containsSqlInjection(input: String): Boolean {
        return SQL_INJECTION_PATTERN.containsMatchIn(input)
    }
    
    /**
     * Validate and sanitize text input to prevent XSS attacks
     * Requirements: 24.3
     */
    fun sanitizeXssInput(input: String): String {
        if (containsXss(input)) {
            Timber.w("Potential XSS attack detected in input")
            // Remove dangerous patterns
            return input.replace(XSS_PATTERN, "")
        }
        return input
    }
    
    /**
     * Check if input contains potential XSS patterns
     */
    fun containsXss(input: String): Boolean {
        return XSS_PATTERN.containsMatchIn(input)
    }
    
    /**
     * Sanitize general text input (combines SQL and XSS sanitization)
     * Requirements: 24.3
     */
    fun sanitizeTextInput(input: String): String {
        var sanitized = input.trim()
        sanitized = sanitizeSqlInput(sanitized)
        sanitized = sanitizeXssInput(sanitized)
        return sanitized
    }
    
    /**
     * Validate phone number format
     * Requirements: 1.6
     */
    fun isValidPhoneNumber(phoneNumber: String): Boolean {
        val cleaned = phoneNumber.replace(Regex("[\\s\\-()]"), "")
        return PHONE_NUMBER_PATTERN.matches(cleaned)
    }
    
    /**
     * Validate email format
     */
    fun isValidEmail(email: String): Boolean {
        return EMAIL_PATTERN.matches(email.trim())
    }
    
    /**
     * Validate alphanumeric input (letters, numbers, spaces only)
     */
    fun isAlphanumeric(input: String): Boolean {
        return ALPHANUMERIC_PATTERN.matches(input)
    }
    
    /**
     * Validate string length
     */
    fun isValidLength(input: String, minLength: Int, maxLength: Int): Boolean {
        val length = input.trim().length
        return length in minLength..maxLength
    }
    
    /**
     * Validate OTP code (6 digits)
     */
    fun isValidOtp(otp: String): Boolean {
        return otp.matches(Regex("^\\d{6}$"))
    }
    
    /**
     * Validate rating value (1-5)
     */
    fun isValidRating(rating: Int): Boolean {
        return rating in 1..5
    }
    
    /**
     * Validate review text length
     * Requirements: 8.2
     */
    fun isValidReview(review: String): Boolean {
        return isValidLength(review, 0, 500)
    }
    
    /**
     * Validate coordinates
     */
    fun isValidLatitude(latitude: Double): Boolean {
        return latitude in -90.0..90.0
    }
    
    fun isValidLongitude(longitude: Double): Boolean {
        return longitude in -180.0..180.0
    }
    
    /**
     * Validate amount (positive, max 2 decimal places)
     */
    fun isValidAmount(amount: Double): Boolean {
        if (amount <= 0) return false
        val decimalPlaces = amount.toString().substringAfter('.', "").length
        return decimalPlaces <= 2
    }
    
    /**
     * Sanitize file name to prevent path traversal attacks
     */
    fun sanitizeFileName(fileName: String): String {
        // Remove path separators and parent directory references
        return fileName
            .replace(Regex("[/\\\\]"), "")
            .replace("..", "")
            .trim()
    }
    
    /**
     * Validate URL format
     */
    fun isValidUrl(url: String): Boolean {
        return try {
            val urlPattern = Regex(
                "^(https?://)?([\\da-z.-]+)\\.([a-z.]{2,6})([/\\w .-]*)*/?$",
                RegexOption.IGNORE_CASE
            )
            urlPattern.matches(url)
        } catch (e: Exception) {
            false
        }
    }
    
    /**
     * Validate that input doesn't contain null bytes
     */
    fun containsNullBytes(input: String): Boolean {
        return input.contains('\u0000')
    }
    
    /**
     * Comprehensive input validation result
     */
    data class ValidationResult(
        val isValid: Boolean,
        val errorMessage: String? = null
    ) {
        companion object {
            fun success() = ValidationResult(true)
            fun failure(message: String) = ValidationResult(false, message)
        }
    }
    
    /**
     * Validate user profile name
     */
    fun validateProfileName(name: String): ValidationResult {
        val sanitized = sanitizeTextInput(name)
        
        return when {
            sanitized.isBlank() -> ValidationResult.failure("Name cannot be empty")
            !isValidLength(sanitized, 2, 50) -> ValidationResult.failure("Name must be 2-50 characters")
            containsNullBytes(sanitized) -> ValidationResult.failure("Invalid characters in name")
            else -> ValidationResult.success()
        }
    }
    
    /**
     * Validate message content
     */
    fun validateMessage(message: String): ValidationResult {
        val sanitized = sanitizeTextInput(message)
        
        return when {
            sanitized.isBlank() -> ValidationResult.failure("Message cannot be empty")
            !isValidLength(sanitized, 1, 1000) -> ValidationResult.failure("Message must be 1-1000 characters")
            containsNullBytes(sanitized) -> ValidationResult.failure("Invalid characters in message")
            else -> ValidationResult.success()
        }
    }
    
    /**
     * Validate address input
     */
    fun validateAddress(address: String): ValidationResult {
        val sanitized = sanitizeTextInput(address)
        
        return when {
            sanitized.isBlank() -> ValidationResult.failure("Address cannot be empty")
            !isValidLength(sanitized, 5, 200) -> ValidationResult.failure("Address must be 5-200 characters")
            containsNullBytes(sanitized) -> ValidationResult.failure("Invalid characters in address")
            else -> ValidationResult.success()
        }
    }
}
