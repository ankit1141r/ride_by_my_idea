package com.rideconnect.core.domain.repository

import com.rideconnect.core.common.result.Result
import com.rideconnect.core.domain.model.AppSettings
import com.rideconnect.core.domain.model.Language
import com.rideconnect.core.domain.model.NotificationPreferences
import com.rideconnect.core.domain.model.Theme
import kotlinx.coroutines.flow.Flow

interface SettingsRepository {
    fun getSettings(): Flow<AppSettings>
    suspend fun updateLanguage(language: Language): Result<Unit>
    suspend fun updateTheme(theme: Theme): Result<Unit>
    suspend fun updateNotificationPreferences(preferences: NotificationPreferences): Result<Unit>
    suspend fun updateParcelDeliveryPreference(accept: Boolean): Result<Unit>
    suspend fun updateExtendedAreaPreference(accept: Boolean): Result<Unit>
    suspend fun resetToDefaults(): Result<Unit>
}
