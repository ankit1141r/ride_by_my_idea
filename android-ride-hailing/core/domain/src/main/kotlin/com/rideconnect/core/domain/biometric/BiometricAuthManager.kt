package com.rideconnect.core.domain.biometric

import com.rideconnect.core.common.result.Result
import com.rideconnect.core.domain.model.AuthToken

/**
 * Manager for biometric authentication functionality.
 * Handles fingerprint and face recognition authentication.
 */
interface BiometricAuthManager {
    /**
     * Checks if biometric authentication is available on the device.
     * @return true if biometric hardware is available and enrolled, false otherwise
     */
    fun isBiometricAvailable(): Boolean
    
    /**
     * Authenticates the user using biometric credentials.
     * @return Result with true if authentication succeeded, false if failed or cancelled
     */
    suspend fun authenticateWithBiometric(): Result<Boolean>
    
    /**
     * Enables biometric authentication for future logins.
     * Stores the auth token securely for biometric access.
     * @param token The authentication token to store
     */
    suspend fun enableBiometric(token: AuthToken)
    
    /**
     * Disables biometric authentication and removes stored credentials.
     */
    suspend fun disableBiometric()
    
    /**
     * Checks if biometric authentication is currently enabled.
     * @return true if biometric auth is enabled, false otherwise
     */
    fun isBiometricEnabled(): Boolean
}
