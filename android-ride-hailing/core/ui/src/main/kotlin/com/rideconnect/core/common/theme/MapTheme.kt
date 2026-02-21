package com.rideconnect.core.common.theme

import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color
import com.rideconnect.core.domain.model.Theme

/**
 * Map-specific theme utilities
 * Requirements: 22.7
 */
object MapTheme {
    
    /**
     * Get marker color for rider based on current theme
     */
    @Composable
    fun getRiderMarkerColor(theme: Theme = Theme.SYSTEM_DEFAULT): Color {
        val isDark = when (theme) {
            Theme.LIGHT -> false
            Theme.DARK -> true
            Theme.SYSTEM_DEFAULT -> isSystemInDarkTheme()
        }
        
        return if (isDark) {
            Color(0xFF64B5F6) // Lighter blue for dark mode
        } else {
            MapMarkerRider // Standard blue for light mode
        }
    }
    
    /**
     * Get marker color for driver based on current theme
     */
    @Composable
    fun getDriverMarkerColor(theme: Theme = Theme.SYSTEM_DEFAULT): Color {
        val isDark = when (theme) {
            Theme.LIGHT -> false
            Theme.DARK -> true
            Theme.SYSTEM_DEFAULT -> isSystemInDarkTheme()
        }
        
        return if (isDark) {
            Color(0xFF81C784) // Lighter green for dark mode
        } else {
            MapMarkerDriver // Standard green for light mode
        }
    }
    
    /**
     * Get route polyline color based on current theme
     */
    @Composable
    fun getRouteColor(theme: Theme = Theme.SYSTEM_DEFAULT): Color {
        val isDark = when (theme) {
            Theme.LIGHT -> false
            Theme.DARK -> true
            Theme.SYSTEM_DEFAULT -> isSystemInDarkTheme()
        }
        
        return if (isDark) {
            DarkPrimary // Use dark theme primary color
        } else {
            MapRouteColor // Use light theme route color
        }
    }
    
    /**
     * Get map style based on current theme
     * Returns map style JSON resource ID
     */
    fun getMapStyle(isDark: Boolean): Int? {
        // Return null for default style in light mode
        // In production, you would return a dark map style resource for dark mode
        return if (isDark) {
            // R.raw.map_style_dark
            null // Placeholder - implement with actual dark map style
        } else {
            null // Use default Google Maps style
        }
    }
}
