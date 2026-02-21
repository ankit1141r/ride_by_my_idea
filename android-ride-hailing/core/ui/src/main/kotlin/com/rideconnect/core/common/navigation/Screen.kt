package com.rideconnect.core.common.navigation

/**
 * Sealed class representing all navigation destinations in the app.
 * Each screen has a unique route string used for navigation.
 */
sealed class Screen(val route: String) {
    // Authentication screens
    object Login : Screen("login")
    object OtpVerification : Screen("otp_verification/{phoneNumber}") {
        fun createRoute(phoneNumber: String) = "otp_verification/$phoneNumber"
    }
    
    // Rider App screens
    object RiderHome : Screen("rider_home")
    object RideRequest : Screen("ride_request")
    object RideTracking : Screen("ride_tracking/{rideId}") {
        fun createRoute(rideId: String) = "ride_tracking/$rideId"
    }
    object ScheduleRide : Screen("schedule_ride")
    object ScheduledRides : Screen("scheduled_rides")
    object ParcelDelivery : Screen("parcel_delivery")
    object ParcelTracking : Screen("parcel_tracking/{deliveryId}") {
        fun createRoute(deliveryId: String) = "parcel_tracking/$deliveryId"
    }
    object RideHistory : Screen("ride_history")
    object RideReceipt : Screen("ride_receipt/{rideId}") {
        fun createRoute(rideId: String) = "ride_receipt/$rideId"
    }
    object Payment : Screen("payment/{rideId}") {
        fun createRoute(rideId: String) = "payment/$rideId"
    }
    object PaymentHistory : Screen("payment_history")
    object Chat : Screen("chat/{rideId}") {
        fun createRoute(rideId: String) = "chat/$rideId"
    }
    
    // Driver App screens
    object DriverHome : Screen("driver_home")
    object ActiveRide : Screen("active_ride/{rideId}") {
        fun createRoute(rideId: String) = "active_ride/$rideId"
    }
    object Earnings : Screen("earnings")
    object DriverRatings : Screen("driver_ratings")
    object DriverSettings : Screen("driver_settings")
    
    // Shared screens
    object Profile : Screen("profile")
    object EmergencyContacts : Screen("emergency_contacts")
    object Settings : Screen("settings")
    object NotificationPreferences : Screen("notification_preferences")
    object RatingHistory : Screen("rating_history")
    
    companion object {
        // Deep link URIs
        const val DEEP_LINK_BASE = "rideconnect://app"
        
        // Deep link routes
        const val DEEP_LINK_RIDE_TRACKING = "$DEEP_LINK_BASE/ride/{rideId}"
        const val DEEP_LINK_CHAT = "$DEEP_LINK_BASE/chat/{rideId}"
        const val DEEP_LINK_PAYMENT = "$DEEP_LINK_BASE/payment/{rideId}"
        const val DEEP_LINK_ACTIVE_RIDE = "$DEEP_LINK_BASE/active_ride/{rideId}"
    }
}
