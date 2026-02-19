package com.rideconnect.core.data.biometric

import android.content.Context
import androidx.biometric.BiometricManager
import androidx.biometric.BiometricPrompt
import androidx.core.content.ContextCompat
import androidx.fragment.app.FragmentActivity
import com.rideconnect.core.data.local.TokenManager
import com.rideconnect.core.domain.biometric.BiometricAuthManager
import com.rideconnect.core.domain.model.AuthToken
import dagger.hilt.android.qualifiers.ApplicationContext
import kotlinx.coroutines.suspendCancellableCoroutine
import timber.log.Timber
import javax.inject.Inject
import kotlin.coroutines.resume

/**
 * Implementation of BiometricAuthManager using Android BiometricPrompt API.
 */
class BiometricAuthManagerImpl @Inject constructor(
    @ApplicationContext private val context: Context,
    private val tokenManager: TokenManager
) : BiometricAuthManager {
    
    private val biometricManager = BiometricManager.from(context)
    private val sharedPreferences = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
    
    override fun isBiometricAvailable(): Boolean {
        return when (biometricManager.canAuthenticate(AUTHENTICATORS)) {
            BiometricManager.BIOMETRIC_SUCCESS -> true
            BiometricManager.BIOMETRIC_ERROR_NO_HARDWARE -> {
                Timber.d("No biometric hardware available")
                false
            }
            BiometricManager.BIOMETRIC_ERROR_HW_UNAVAILABLE -> {
                Timber.d("Biometric hardware unavailable")
                false
            }
            BiometricManager.BIOMETRIC_ERROR_NONE_ENROLLED -> {
                Timber.d("No biometric credentials enrolled")
                false
            }
            else -> false
        }
    }
    
    override suspend fun authenticateWithBiometric(): Result<Boolean> = suspendCancellableCoroutine { continuation ->
        if (!isBiometricAvailable()) {
            continuation.resume(Result.failure(BiometricNotAvailableException()))
            return@suspendCancellableCoroutine
        }
        
        if (!isBiometricEnabled()) {
            continuation.resume(Result.failure(BiometricNotEnabledException()))
            return@suspendCancellableCoroutine
        }
        
        // Get the current activity context
        val activity = context as? FragmentActivity
        if (activity == null) {
            continuation.resume(Result.failure(IllegalStateException("Context is not a FragmentActivity")))
            return@suspendCancellableCoroutine
        }
        
        val executor = ContextCompat.getMainExecutor(context)
        
        val promptInfo = BiometricPrompt.PromptInfo.Builder()
            .setTitle("Biometric Authentication")
            .setSubtitle("Log in using your biometric credential")
            .setNegativeButtonText("Use OTP instead")
            .setAllowedAuthenticators(AUTHENTICATORS)
            .build()
        
        val biometricPrompt = BiometricPrompt(activity, executor,
            object : BiometricPrompt.AuthenticationCallback() {
                override fun onAuthenticationError(errorCode: Int, errString: CharSequence) {
                    super.onAuthenticationError(errorCode, errString)
                    Timber.e("Biometric authentication error: $errString")
                    if (continuation.isActive) {
                        continuation.resume(Result.success(false))
                    }
                }
                
                override fun onAuthenticationSucceeded(result: BiometricPrompt.AuthenticationResult) {
                    super.onAuthenticationSucceeded(result)
                    Timber.d("Biometric authentication succeeded")
                    if (continuation.isActive) {
                        continuation.resume(Result.success(true))
                    }
                }
                
                override fun onAuthenticationFailed() {
                    super.onAuthenticationFailed()
                    Timber.w("Biometric authentication failed")
                    // Don't resume here - let user retry
                }
            })
        
        biometricPrompt.authenticate(promptInfo)
        
        continuation.invokeOnCancellation {
            biometricPrompt.cancelAuthentication()
        }
    }
    
    override suspend fun enableBiometric(token: AuthToken) {
        if (!isBiometricAvailable()) {
            throw BiometricNotAvailableException()
        }
        
        // Store the token securely
        tokenManager.saveToken(token)
        
        // Mark biometric as enabled
        sharedPreferences.edit()
            .putBoolean(KEY_BIOMETRIC_ENABLED, true)
            .apply()
        
        Timber.d("Biometric authentication enabled")
    }
    
    override suspend fun disableBiometric() {
        sharedPreferences.edit()
            .putBoolean(KEY_BIOMETRIC_ENABLED, false)
            .apply()
        
        Timber.d("Biometric authentication disabled")
    }
    
    override fun isBiometricEnabled(): Boolean {
        return sharedPreferences.getBoolean(KEY_BIOMETRIC_ENABLED, false)
    }
    
    companion object {
        private const val PREFS_NAME = "biometric_prefs"
        private const val KEY_BIOMETRIC_ENABLED = "biometric_enabled"
        private const val AUTHENTICATORS = BiometricManager.Authenticators.BIOMETRIC_STRONG
    }
}

class BiometricNotAvailableException : Exception("Biometric authentication is not available on this device")
class BiometricNotEnabledException : Exception("Biometric authentication is not enabled")
