package com.rideconnect.core.common.util

/**
 * Utility for formatting addresses for display with smart truncation.
 * 
 * Handles long addresses gracefully, especially at large text sizes,
 * while maintaining accessibility and full address availability.
 */
object AddressFormatter {
    
    /**
     * Maximum characters for address display before truncation.
     */
    private const val MAX_DISPLAY_LENGTH = 60
    
    /**
     * Maximum characters for short address display (e.g., in lists).
     */
    private const val MAX_SHORT_LENGTH = 40
    
    /**
     * Formats an address for display with smart truncation.
     * 
     * @param address The full address string
     * @param maxLength Maximum length before truncation (default: MAX_DISPLAY_LENGTH)
     * @return Formatted address, truncated if necessary
     */
    fun formatAddress(address: String, maxLength: Int = MAX_DISPLAY_LENGTH): String {
        if (address.length <= maxLength) {
            return address
        }
        
        // Try to truncate at a natural break point (comma, space)
        val truncated = address.substring(0, maxLength)
        val lastComma = truncated.lastIndexOf(',')
        val lastSpace = truncated.lastIndexOf(' ')
        
        val breakPoint = when {
            lastComma > maxLength * 0.7 -> lastComma
            lastSpace > maxLength * 0.7 -> lastSpace
            else -> maxLength
        }
        
        return address.substring(0, breakPoint).trim() + "..."
    }
    
    /**
     * Formats an address for short display (e.g., in lists).
     * 
     * @param address The full address string
     * @return Short formatted address
     */
    fun formatShortAddress(address: String): String {
        return formatAddress(address, MAX_SHORT_LENGTH)
    }
    
    /**
     * Extracts the main part of an address (before first comma).
     * Useful for displaying just the street name or building.
     * 
     * @param address The full address string
     * @return Main part of address
     */
    fun extractMainAddress(address: String): String {
        val commaIndex = address.indexOf(',')
        return if (commaIndex > 0) {
            address.substring(0, commaIndex).trim()
        } else {
            formatShortAddress(address)
        }
    }
    
    /**
     * Formats an address for accessibility (screen readers).
     * Replaces abbreviations and adds pauses for better pronunciation.
     * 
     * @param address The full address string
     * @return Accessibility-friendly address
     */
    fun formatForAccessibility(address: String): String {
        return address
            .replace("St.", "Street")
            .replace("Ave.", "Avenue")
            .replace("Rd.", "Road")
            .replace("Blvd.", "Boulevard")
            .replace("Dr.", "Drive")
            .replace("Ln.", "Lane")
            .replace("Apt.", "Apartment")
            .replace("Ste.", "Suite")
            .replace(",", ", ") // Add space after comma for better pause
    }
    
    /**
     * Checks if an address needs truncation at the given text size.
     * 
     * @param address The address string
     * @param textSizeScale The text size scale (1.0 = 100%, 2.0 = 200%)
     * @return True if address should be truncated
     */
    fun needsTruncation(address: String, textSizeScale: Float): Boolean {
        val adjustedMaxLength = (MAX_DISPLAY_LENGTH / textSizeScale).toInt()
        return address.length > adjustedMaxLength
    }
}
