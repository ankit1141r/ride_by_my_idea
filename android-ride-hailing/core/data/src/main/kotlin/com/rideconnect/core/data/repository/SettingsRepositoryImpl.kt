package com.rideconnect.core.data.repository

import android.content.Context
import androidx.datastore.core.DataStore
import androidx.datastore.preferences.core.Preferences
import androidx.datastore.preferences.core.booleanPreferencesKey
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.stringPreferencesKey
import androidx.datastore.preferences.preferencesDataStore
import com.rideconnect.core.common.result.Result
import com.rideconnect.core.domain.model.AppSettings
import com.rideconnect.core.domain.model.Language
import com.rideconnect.core.domain.model.NotificationPreferences
import com.rideconnect.core.domain.model.Theme
import com.rideconnect.core.domain.repository.SettingsRepository
import dagger.hilt.android.qualifiers.ApplicationContext
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.catch
import kotlinx.coroutines.flow.map
import javax.inject.Inject
import javax.inject.Singleton

private val Context.dataStore: DataStore<Preferences> by preferencesDataStore(name = "settings")

@Singleton
class SettingsRepositoryImpl @Inject constructor(
    @ApplicationContext private val context: Context
) : SettingsRepository {

    private object PreferencesKeys {
        val LANGUAGE = stringPreferencesKey("language")
        val THEME = stringPreferencesKey("theme")
        
        // Notification preferences
        val NOTIF_RIDE_ACCEPTED = booleanPreferencesKey("notif_ride_accepted")
        val NOTIF_DRIVER_ARRIVING = booleanPreferencesKey("notif_driver_arriving")
        val NOTIF_DRIVER_ARRIVED = booleanPreferencesKey("notif_driver_arrived")
        val NOTIF_RIDE_STARTED = booleanPreferencesKey("notif_ride_started")
        val NOTIF_RIDE_COMPLETED = booleanPreferencesKey("notif_ride_completed")
        val NOTIF_RIDE_CANCELLED = booleanPreferencesKey("notif_ride_cancelled")
        val NOTIF_NEW_RIDE_REQUEST = booleanPreferencesKey("notif_new_ride_request")
        val NOTIF_CHAT_MESSAGE = booleanPreferencesKey("notif_chat_message")
        val NOTIF_PAYMENT_SUCCESS = booleanPreferencesKey("notif_payment_success")
        val NOTIF_PAYMENT_FAILED = booleanPreferencesKey("notif_payment_failed")
        val NOTIF_SCHEDULED_RIDE_REMINDER = booleanPreferencesKey("notif_scheduled_ride_reminder")
        
        // Driver preferences
        val ACCEPT_PARCEL_DELIVERY = booleanPreferencesKey("accept_parcel_delivery")
        val ACCEPT_EXTENDED_AREA = booleanPreferencesKey("accept_extended_area")
    }

    override fun getSettings(): Flow<AppSettings> {
        return context.dataStore.data
            .catch { emit(androidx.datastore.preferences.core.emptyPreferences()) }
            .map { preferences ->
                AppSettings(
                    language = preferences[PreferencesKeys.LANGUAGE]?.let { 
                        Language.valueOf(it) 
                    } ?: Language.SYSTEM_DEFAULT,
                    theme = preferences[PreferencesKeys.THEME]?.let { 
                        Theme.valueOf(it) 
                    } ?: Theme.SYSTEM_DEFAULT,
                    notificationPreferences = NotificationPreferences(
                        rideAccepted = preferences[PreferencesKeys.NOTIF_RIDE_ACCEPTED] ?: true,
                        driverArriving = preferences[PreferencesKeys.NOTIF_DRIVER_ARRIVING] ?: true,
                        driverArrived = preferences[PreferencesKeys.NOTIF_DRIVER_ARRIVED] ?: true,
                        rideStarted = preferences[PreferencesKeys.NOTIF_RIDE_STARTED] ?: true,
                        rideCompleted = preferences[PreferencesKeys.NOTIF_RIDE_COMPLETED] ?: true,
                        rideCancelled = preferences[PreferencesKeys.NOTIF_RIDE_CANCELLED] ?: true,
                        newRideRequest = preferences[PreferencesKeys.NOTIF_NEW_RIDE_REQUEST] ?: true,
                        chatMessage = preferences[PreferencesKeys.NOTIF_CHAT_MESSAGE] ?: true,
                        paymentSuccess = preferences[PreferencesKeys.NOTIF_PAYMENT_SUCCESS] ?: true,
                        paymentFailed = preferences[PreferencesKeys.NOTIF_PAYMENT_FAILED] ?: true,
                        scheduledRideReminder = preferences[PreferencesKeys.NOTIF_SCHEDULED_RIDE_REMINDER] ?: true
                    ),
                    acceptParcelDelivery = preferences[PreferencesKeys.ACCEPT_PARCEL_DELIVERY] ?: false,
                    acceptExtendedArea = preferences[PreferencesKeys.ACCEPT_EXTENDED_AREA] ?: false
                )
            }
    }

    override suspend fun updateLanguage(language: Language): Result<Unit> {
        return try {
            context.dataStore.edit { preferences ->
                preferences[PreferencesKeys.LANGUAGE] = language.name
            }
            Result.Success(Unit)
        } catch (e: Exception) {
            Result.Error(e)
        }
    }

    override suspend fun updateTheme(theme: Theme): Result<Unit> {
        return try {
            context.dataStore.edit { preferences ->
                preferences[PreferencesKeys.THEME] = theme.name
            }
            Result.Success(Unit)
        } catch (e: Exception) {
            Result.Error(e)
        }
    }

    override suspend fun updateNotificationPreferences(preferences: NotificationPreferences): Result<Unit> {
        return try {
            context.dataStore.edit { prefs ->
                prefs[PreferencesKeys.NOTIF_RIDE_ACCEPTED] = preferences.rideAccepted
                prefs[PreferencesKeys.NOTIF_DRIVER_ARRIVING] = preferences.driverArriving
                prefs[PreferencesKeys.NOTIF_DRIVER_ARRIVED] = preferences.driverArrived
                prefs[PreferencesKeys.NOTIF_RIDE_STARTED] = preferences.rideStarted
                prefs[PreferencesKeys.NOTIF_RIDE_COMPLETED] = preferences.rideCompleted
                prefs[PreferencesKeys.NOTIF_RIDE_CANCELLED] = preferences.rideCancelled
                prefs[PreferencesKeys.NOTIF_NEW_RIDE_REQUEST] = preferences.newRideRequest
                prefs[PreferencesKeys.NOTIF_CHAT_MESSAGE] = preferences.chatMessage
                prefs[PreferencesKeys.NOTIF_PAYMENT_SUCCESS] = preferences.paymentSuccess
                prefs[PreferencesKeys.NOTIF_PAYMENT_FAILED] = preferences.paymentFailed
                prefs[PreferencesKeys.NOTIF_SCHEDULED_RIDE_REMINDER] = preferences.scheduledRideReminder
            }
            Result.Success(Unit)
        } catch (e: Exception) {
            Result.Error(e)
        }
    }

    override suspend fun updateParcelDeliveryPreference(accept: Boolean): Result<Unit> {
        return try {
            context.dataStore.edit { preferences ->
                preferences[PreferencesKeys.ACCEPT_PARCEL_DELIVERY] = accept
            }
            Result.Success(Unit)
        } catch (e: Exception) {
            Result.Error(e)
        }
    }

    override suspend fun updateExtendedAreaPreference(accept: Boolean): Result<Unit> {
        return try {
            context.dataStore.edit { preferences ->
                preferences[PreferencesKeys.ACCEPT_EXTENDED_AREA] = accept
            }
            Result.Success(Unit)
        } catch (e: Exception) {
            Result.Error(e)
        }
    }

    override suspend fun resetToDefaults(): Result<Unit> {
        return try {
            context.dataStore.edit { preferences ->
                preferences.clear()
            }
            Result.Success(Unit)
        } catch (e: Exception) {
            Result.Error(e)
        }
    }
}
