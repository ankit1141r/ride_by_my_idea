package com.rideconnect.core.domain.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.rideconnect.core.domain.model.AuthToken
import com.rideconnect.core.domain.model.User
import com.rideconnect.core.domain.repository.AuthRepository
import com.rideconnect.core.domain.validation.PhoneNumberValidator
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import timber.log.Timber
import javax.inject.Inject

@HiltViewModel
class AuthViewModel @Inject constructor(
    private val authRepository: AuthRepository,
    private val phoneNumberValidator: PhoneNumberValidator,
    private val biometricAuthManager: com.rideconnect.core.domain.biometric.BiometricAuthManager
) : ViewModel() {
    
    private val _authState = MutableStateFlow<AuthState>(AuthState.Initial)
    val authState: StateFlow<AuthState> = _authState.asStateFlow()
    
    private val _phoneNumber = MutableStateFlow("")
    val phoneNumber: StateFlow<String> = _phoneNumber.asStateFlow()
    
    private val _otp = MutableStateFlow("")
    val otp: StateFlow<String> = _otp.asStateFlow()
    
    init {
        checkAuthStatus()
    }
    
    private fun checkAuthStatus() {
        val token = authRepository.getStoredToken()
        val user = authRepository.getStoredUser()
        
        if (token != null && user != null) {
            _authState.value = AuthState.Authenticated(user, token)
        } else {
            _authState.value = AuthState.Unauthenticated
        }
    }
    
    fun updatePhoneNumber(phone: String) {
        _phoneNumber.value = phone
    }
    
    fun updateOtp(otpValue: String) {
        _otp.value = otpValue
    }
    
    fun sendOtp() {
        val phone = _phoneNumber.value.trim()
        
        // Validate phone number format
        if (!phoneNumberValidator.isValid(phone)) {
            _authState.value = AuthState.Error("Invalid phone number format. Please enter a valid phone number.")
            return
        }
        
        viewModelScope.launch {
            _authState.value = AuthState.Loading
            
            val result = authRepository.sendOtp(phone)
            
            result.fold(
                onSuccess = {
                    _authState.value = AuthState.OtpSent(phone)
                    Timber.d("OTP sent successfully to $phone")
                },
                onFailure = { error ->
                    val errorMessage = when {
                        error.message?.contains("network", ignoreCase = true) == true ->
                            "Network error. Please check your connection and try again."
                        else -> error.message ?: "Failed to send OTP. Please try again."
                    }
                    _authState.value = AuthState.Error(errorMessage)
                    Timber.e(error, "Failed to send OTP")
                }
            )
        }
    }
    
    fun verifyOtp() {
        val phone = _phoneNumber.value.trim()
        val otpValue = _otp.value.trim()
        
        if (otpValue.isEmpty() || otpValue.length != 6) {
            _authState.value = AuthState.Error("Please enter a valid 6-digit OTP")
            return
        }
        
        viewModelScope.launch {
            _authState.value = AuthState.Loading
            
            val result = authRepository.verifyOtp(phone, otpValue)
            
            result.fold(
                onSuccess = { (token, user) ->
                    _authState.value = AuthState.Authenticated(user, token)
                    Timber.d("OTP verified successfully for user ${user.id}")
                },
                onFailure = { error ->
                    val errorMessage = when {
                        error.message?.contains("invalid", ignoreCase = true) == true ||
                        error.message?.contains("incorrect", ignoreCase = true) == true ->
                            "Invalid OTP. Please check and try again."
                        error.message?.contains("expired", ignoreCase = true) == true ->
                            "OTP has expired. Please request a new one."
                        error.message?.contains("network", ignoreCase = true) == true ->
                            "Network error. Please check your connection and try again."
                        else -> error.message ?: "Failed to verify OTP. Please try again."
                    }
                    _authState.value = AuthState.Error(errorMessage)
                    Timber.e(error, "Failed to verify OTP")
                }
            )
        }
    }
    
    fun isBiometricAvailable(): Boolean {
        return biometricAuthManager.isBiometricAvailable()
    }
    
    fun isBiometricEnabled(): Boolean {
        return biometricAuthManager.isBiometricEnabled()
    }
    
    fun loginWithBiometric() {
        if (!biometricAuthManager.isBiometricAvailable()) {
            _authState.value = AuthState.Error("Biometric authentication is not available on this device")
            return
        }
        
        if (!biometricAuthManager.isBiometricEnabled()) {
            _authState.value = AuthState.Error("Biometric authentication is not enabled. Please log in with OTP first.")
            return
        }
        
        viewModelScope.launch {
            _authState.value = AuthState.Loading
            
            val result = biometricAuthManager.authenticateWithBiometric()
            
            result.fold(
                onSuccess = { authenticated ->
                    if (authenticated) {
                        // Biometric authentication successful, retrieve stored token
                        val token = authRepository.getStoredToken()
                        val user = authRepository.getStoredUser()
                        
                        if (token != null && user != null) {
                            _authState.value = AuthState.Authenticated(user, token)
                            Timber.d("Biometric login successful for user ${user.id}")
                        } else {
                            _authState.value = AuthState.Error("Session expired. Please log in with OTP.")
                        }
                    } else {
                        // User cancelled or authentication failed
                        _authState.value = AuthState.Unauthenticated
                        Timber.d("Biometric authentication cancelled or failed")
                    }
                },
                onFailure = { error ->
                    val errorMessage = error.message ?: "Biometric authentication failed. Please try OTP login."
                    _authState.value = AuthState.Error(errorMessage)
                    Timber.e(error, "Biometric authentication error")
                }
            )
        }
    }
    
    fun enableBiometric() {
        val currentState = _authState.value
        if (currentState !is AuthState.Authenticated) {
            Timber.w("Cannot enable biometric - user not authenticated")
            return
        }
        
        if (!biometricAuthManager.isBiometricAvailable()) {
            _authState.value = AuthState.Error("Biometric authentication is not available on this device")
            return
        }
        
        viewModelScope.launch {
            try {
                biometricAuthManager.enableBiometric(currentState.token)
                Timber.d("Biometric authentication enabled successfully")
            } catch (e: Exception) {
                Timber.e(e, "Failed to enable biometric authentication")
            }
        }
    }
    
    fun disableBiometric() {
        viewModelScope.launch {
            try {
                biometricAuthManager.disableBiometric()
                Timber.d("Biometric authentication disabled successfully")
            } catch (e: Exception) {
                Timber.e(e, "Failed to disable biometric authentication")
            }
        }
    }
    
    fun logout() {
        viewModelScope.launch {
            _authState.value = AuthState.Loading
            
            val result = authRepository.logout()
            
            result.fold(
                onSuccess = {
                    _authState.value = AuthState.Unauthenticated
                    _phoneNumber.value = ""
                    _otp.value = ""
                    Timber.d("Logout successful")
                },
                onFailure = { error ->
                    // Even if logout API fails, we still clear local data
                    _authState.value = AuthState.Unauthenticated
                    _phoneNumber.value = ""
                    _otp.value = ""
                    Timber.e(error, "Logout API failed but local data cleared")
                }
            )
        }
    }
    
    fun clearError() {
        if (_authState.value is AuthState.Error) {
            _authState.value = AuthState.Unauthenticated
        }
    }
    
    fun retryLastAction() {
        when (val currentState = _authState.value) {
            is AuthState.OtpSent -> verifyOtp()
            is AuthState.Error -> {
                // Determine what to retry based on current data
                if (_otp.value.isNotEmpty()) {
                    verifyOtp()
                } else if (_phoneNumber.value.isNotEmpty()) {
                    sendOtp()
                }
            }
            else -> {
                // No action to retry
            }
        }
    }
}

sealed class AuthState {
    object Initial : AuthState()
    object Loading : AuthState()
    object Unauthenticated : AuthState()
    data class OtpSent(val phoneNumber: String) : AuthState()
    data class Authenticated(val user: User, val token: AuthToken) : AuthState()
    data class Error(val message: String) : AuthState()
}
