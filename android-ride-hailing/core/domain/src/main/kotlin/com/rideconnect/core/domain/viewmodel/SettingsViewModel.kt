package com.rideconnect.core.domain.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.rideconnect.core.common.result.Result
import com.rideconnect.core.domain.model.AppSettings
import com.rideconnect.core.domain.model.Language
import com.rideconnect.core.domain.model.NotificationPreferences
import com.rideconnect.core.domain.model.Theme
import com.rideconnect.core.domain.repository.SettingsRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.catch
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class SettingsViewModel @Inject constructor(
    private val settingsRepository: SettingsRepository
) : ViewModel() {

    private val _settings = MutableStateFlow(AppSettings())
    val settings: StateFlow<AppSettings> = _settings.asStateFlow()

    private val _updateStatus = MutableStateFlow<UpdateStatus>(UpdateStatus.Idle)
    val updateStatus: StateFlow<UpdateStatus> = _updateStatus.asStateFlow()

    init {
        loadSettings()
    }

    private fun loadSettings() {
        viewModelScope.launch {
            settingsRepository.getSettings()
                .catch { e ->
                    _updateStatus.value = UpdateStatus.Error(e.message ?: "Failed to load settings")
                }
                .collect { appSettings ->
                    _settings.value = appSettings
                }
        }
    }

    fun updateLanguage(language: Language) {
        viewModelScope.launch {
            _updateStatus.value = UpdateStatus.Loading
            when (val result = settingsRepository.updateLanguage(language)) {
                is Result.Success -> {
                    _updateStatus.value = UpdateStatus.Success("Language updated")
                }
                is Result.Error -> {
                    _updateStatus.value = UpdateStatus.Error(
                        result.exception.message ?: "Failed to update language"
                    )
                }
            }
        }
    }

    fun updateTheme(theme: Theme) {
        viewModelScope.launch {
            _updateStatus.value = UpdateStatus.Loading
            when (val result = settingsRepository.updateTheme(theme)) {
                is Result.Success -> {
                    _updateStatus.value = UpdateStatus.Success("Theme updated")
                }
                is Result.Error -> {
                    _updateStatus.value = UpdateStatus.Error(
                        result.exception.message ?: "Failed to update theme"
                    )
                }
            }
        }
    }

    fun updateNotificationPreferences(preferences: NotificationPreferences) {
        viewModelScope.launch {
            _updateStatus.value = UpdateStatus.Loading
            when (val result = settingsRepository.updateNotificationPreferences(preferences)) {
                is Result.Success -> {
                    _updateStatus.value = UpdateStatus.Success("Notification preferences updated")
                }
                is Result.Error -> {
                    _updateStatus.value = UpdateStatus.Error(
                        result.exception.message ?: "Failed to update notification preferences"
                    )
                }
            }
        }
    }

    fun updateParcelDeliveryPreference(accept: Boolean) {
        viewModelScope.launch {
            _updateStatus.value = UpdateStatus.Loading
            when (val result = settingsRepository.updateParcelDeliveryPreference(accept)) {
                is Result.Success -> {
                    _updateStatus.value = UpdateStatus.Success("Parcel delivery preference updated")
                }
                is Result.Error -> {
                    _updateStatus.value = UpdateStatus.Error(
                        result.exception.message ?: "Failed to update parcel delivery preference"
                    )
                }
            }
        }
    }

    fun updateExtendedAreaPreference(accept: Boolean) {
        viewModelScope.launch {
            _updateStatus.value = UpdateStatus.Loading
            when (val result = settingsRepository.updateExtendedAreaPreference(accept)) {
                is Result.Success -> {
                    _updateStatus.value = UpdateStatus.Success("Extended area preference updated")
                }
                is Result.Error -> {
                    _updateStatus.value = UpdateStatus.Error(
                        result.exception.message ?: "Failed to update extended area preference"
                    )
                }
            }
        }
    }

    fun resetToDefaults() {
        viewModelScope.launch {
            _updateStatus.value = UpdateStatus.Loading
            when (val result = settingsRepository.resetToDefaults()) {
                is Result.Success -> {
                    _updateStatus.value = UpdateStatus.Success("Settings reset to defaults")
                }
                is Result.Error -> {
                    _updateStatus.value = UpdateStatus.Error(
                        result.exception.message ?: "Failed to reset settings"
                    )
                }
            }
        }
    }

    fun clearUpdateStatus() {
        _updateStatus.value = UpdateStatus.Idle
    }

    sealed class UpdateStatus {
        object Idle : UpdateStatus()
        object Loading : UpdateStatus()
        data class Success(val message: String) : UpdateStatus()
        data class Error(val message: String) : UpdateStatus()
    }
}
