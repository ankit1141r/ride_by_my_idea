package com.rideconnect.core.domain.validation

/**
 * Phone Number Validator
 * 
 * Validates phone numbers according to Indian mobile number format:
 * - Must start with +91 (India country code)
 * - Followed by 10 digits
 * - First digit of mobile number must be 6-9
 * 
 * Valid format: +91XXXXXXXXXX where X is a digit and first X is 6-9
 * Example: +919876543210
 */
object PhoneNumberValidator {
    
    private val PHONE_NUMBER_REGEX = Regex("^\\+91[6-9]\\d{9}$")
    
    /**
     * Validates if the given phone number is in valid Indian mobile format
     * 
     * @param phoneNumber The phone number to validate
     * @return true if valid, false otherwise
     */
    fun isValid(phoneNumber: String): Boolean {
        if (phoneNumber.isBlank()) {
            return false
        }
        
        return PHONE_NUMBER_REGEX.matches(phoneNumber.trim())
    }
    
    /**
     * Formats a phone number by removing spaces and ensuring proper format
     * 
     * @param phoneNumber The phone number to format
     * @return Formatted phone number or null if invalid
     */
    fun format(phoneNumber: String): String? {
        val cleaned = phoneNumber.replace("\\s+".toRegex(), "")
        
        // If it starts with 91 but not +91, add the +
        val withPlus = if (cleaned.startsWith("91") && !cleaned.startsWith("+91")) {
            "+$cleaned"
        } else if (!cleaned.startsWith("+")) {
            "+91$cleaned"
        } else {
            cleaned
        }
        
        return if (isValid(withPlus)) withPlus else null
    }
    
    /**
     * Extracts the 10-digit mobile number without country code
     * 
     * @param phoneNumber The full phone number with country code
     * @return 10-digit mobile number or null if invalid
     */
    fun extractMobileNumber(phoneNumber: String): String? {
        return if (isValid(phoneNumber)) {
            phoneNumber.substring(3) // Remove +91
        } else {
            null
        }
    }
}
