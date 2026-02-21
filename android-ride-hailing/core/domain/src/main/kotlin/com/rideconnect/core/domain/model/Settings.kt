package com.rideconnect.core.domain.model

data class NotificationPreferences(
    val rideAccepted: Boolean = true,
    val driverArriving: Boolean = true,
    val driverArrived: Boolean = true,
    val rideStarted: Boolean = true,
    val rideCompleted: Boolean = true,
    val rideCancelled: Boolean = true,
    val newRideRequest: Boolean = true,
    val chatMessage: Boolean = true,
    val paymentSuccess: Boolean = true,
    val paymentFailed: Boolean = true,
    val scheduledRideReminder: Boolean = true
)

data class AppSettings(
    val language: Language = Language.SYSTEM_DEFAULT,
    val theme: Theme = Theme.SYSTEM_DEFAULT,
    val notificationPreferences: NotificationPreferences = NotificationPreferences(),
    val acceptParcelDelivery: Boolean = false,
    val acceptExtendedArea: Boolean = false
)

enum class Language {
    ENGLISH,
    HINDI,
    SYSTEM_DEFAULT
}

enum class Theme {
    LIGHT,
    DARK,
    SYSTEM_DEFAULT
}
