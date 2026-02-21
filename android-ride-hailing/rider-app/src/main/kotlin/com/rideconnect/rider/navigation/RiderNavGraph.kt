package com.rideconnect.rider.navigation

import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.navigation.NavHostController
import androidx.navigation.NavType
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.navArgument
import androidx.navigation.navDeepLink
import com.rideconnect.core.common.navigation.Screen
import com.rideconnect.core.common.ui.*
import com.rideconnect.core.domain.viewmodel.*
import com.rideconnect.rider.ui.auth.LoginScreen
import com.rideconnect.rider.ui.auth.OtpVerificationScreen
import com.rideconnect.rider.ui.main.MainScreen

/**
 * Navigation graph for the Rider App.
 * Defines all navigation routes, arguments, and deep links.
 */
@Composable
fun RiderNavGraph(
    navController: NavHostController,
    modifier: Modifier = Modifier,
    startDestination: String = Screen.Login.route
) {
    NavHost(
        navController = navController,
        startDestination = startDestination,
        modifier = modifier
    ) {
        // Authentication flow
        composable(Screen.Login.route) {
            val viewModel: AuthViewModel = hiltViewModel()
            LoginScreen(
                onNavigateToOtpVerification = {
                    navController.navigate(Screen.OtpVerification.createRoute("")) // Will use viewModel's phone number
                },
                onLoginSuccess = {
                    navController.navigate(Screen.RiderHome.route) {
                        popUpTo(Screen.Login.route) { inclusive = true }
                    }
                }
            )
        }
        
        composable(
            route = Screen.OtpVerification.route,
            arguments = listOf(
                navArgument("phoneNumber") { type = NavType.StringType }
            )
        ) { backStackEntry ->
            val viewModel: AuthViewModel = hiltViewModel()
            OtpVerificationScreen(
                onNavigateBack = { navController.popBackStack() },
                onVerificationSuccess = {
                    navController.navigate(Screen.RiderHome.route) {
                        popUpTo(Screen.Login.route) { inclusive = true }
                    }
                }
            )
        }
        
        // Home screen with bottom navigation
        composable(Screen.RiderHome.route) {
            MainScreen(mainNavController = navController)
        }
        
        // Ride request flow
        composable(Screen.RideRequest.route) {
            val viewModel: RideViewModel = hiltViewModel()
            RideRequestScreen(
                viewModel = viewModel,
                onNavigateToLocationSearch = { isPickup ->
                    // TODO: Implement location search navigation
                },
                onNavigateToTracking = {
                    // Navigate to tracking when ride is created
                    viewModel.activeRide.value?.let { ride ->
                        navController.navigate(Screen.RideTracking.createRoute(ride.id)) {
                            popUpTo(Screen.RiderHome.route)
                        }
                    }
                }
            )
        }
        
        // Ride tracking with deep link
        composable(
            route = Screen.RideTracking.route,
            arguments = listOf(
                navArgument("rideId") { type = NavType.StringType }
            ),
            deepLinks = listOf(
                navDeepLink { uriPattern = Screen.DEEP_LINK_RIDE_TRACKING }
            )
        ) { backStackEntry ->
            val rideId = backStackEntry.arguments?.getString("rideId") ?: ""
            val viewModel: RideViewModel = hiltViewModel()
            
            // Load the ride by ID
            LaunchedEffect(rideId) {
                viewModel.loadRide(rideId)
            }
            
            RideTrackingScreen(
                viewModel = viewModel,
                onNavigateBack = { navController.popBackStack() }
            )
        }
        
        // Scheduled rides
        composable(Screen.ScheduleRide.route) {
            val viewModel: ScheduledRideViewModel = hiltViewModel()
            ScheduleRideScreen(
                viewModel = viewModel,
                onNavigateBack = { navController.popBackStack() },
                onSelectPickupLocation = {
                    // TODO: Implement location picker
                },
                onSelectDropoffLocation = {
                    // TODO: Implement location picker
                }
            )
        }
        
        composable(Screen.ScheduledRides.route) {
            val viewModel: ScheduledRideViewModel = hiltViewModel()
            ScheduledRidesScreen(
                viewModel = viewModel,
                onScheduleNewRide = {
                    navController.navigate(Screen.ScheduleRide.route)
                },
                onRideClick = { ride ->
                    // TODO: Navigate to ride details
                }
            )
        }
        
        // Parcel delivery
        composable(Screen.ParcelDelivery.route) {
            val viewModel: ParcelViewModel = hiltViewModel()
            ParcelDeliveryScreen(
                viewModel = viewModel,
                onNavigateToLocationPicker = { isPickup ->
                    // TODO: Implement location picker
                },
                onNavigateBack = { navController.popBackStack() }
            )
        }
        
        composable(
            route = Screen.ParcelTracking.route,
            arguments = listOf(
                navArgument("deliveryId") { type = NavType.StringType }
            )
        ) { backStackEntry ->
            val deliveryId = backStackEntry.arguments?.getString("deliveryId") ?: ""
            val viewModel: ParcelViewModel = hiltViewModel()
            ParcelTrackingScreen(
                viewModel = viewModel,
                parcelId = deliveryId,
                onNavigateBack = { navController.popBackStack() },
                onCallDriver = { phoneNumber ->
                    // TODO: Implement call driver
                }
            )
        }
        
        // Ride history and receipts
        composable(Screen.RideHistory.route) {
            val viewModel: RideViewModel = hiltViewModel()
            val rides by viewModel.rideHistory.collectAsState()
            val isLoading by viewModel.isLoading.collectAsState()
            
            RideHistoryScreen(
                rides = rides,
                isLoading = isLoading,
                onRideClick = { ride ->
                    navController.navigate(Screen.RideReceipt.createRoute(ride.id))
                },
                onSearchQueryChange = { query ->
                    // TODO: Implement search
                },
                onDateRangeSelected = { start, end ->
                    // TODO: Implement date filter
                }
            )
        }
        
        composable(
            route = Screen.RideReceipt.route,
            arguments = listOf(
                navArgument("rideId") { type = NavType.StringType }
            )
        ) { backStackEntry ->
            val rideId = backStackEntry.arguments?.getString("rideId") ?: ""
            val viewModel: RideViewModel = hiltViewModel()
            val rides by viewModel.rideHistory.collectAsState()
            val ride = rides.find { it.id == rideId }
            
            ride?.let {
                RideReceiptScreen(
                    ride = it,
                    driverName = it.driverName,
                    driverPhone = it.driverPhone,
                    onShareClick = {
                        // TODO: Implement share
                    },
                    onBackClick = { navController.popBackStack() }
                )
            }
        }
        
        // Payment flow with deep link
        composable(
            route = Screen.Payment.route,
            arguments = listOf(
                navArgument("rideId") { type = NavType.StringType }
            ),
            deepLinks = listOf(
                navDeepLink { uriPattern = Screen.DEEP_LINK_PAYMENT }
            )
        ) { backStackEntry ->
            val rideId = backStackEntry.arguments?.getString("rideId") ?: ""
            val viewModel: PaymentViewModel = hiltViewModel()
            val uiState by viewModel.uiState.collectAsState()
            val fareBreakdown by viewModel.fareBreakdown.collectAsState()
            
            fareBreakdown?.let { fare ->
                PaymentScreen(
                    rideId = rideId,
                    fareBreakdown = fare,
                    uiState = uiState,
                    onProcessPayment = { id, amount, method ->
                        viewModel.processPayment(id, amount, method)
                    },
                    onNavigateBack = { navController.popBackStack() },
                    onViewReceipt = {
                        navController.navigate(Screen.RideReceipt.createRoute(rideId)) {
                            popUpTo(Screen.RiderHome.route)
                        }
                    }
                )
            }
        }
        
        composable(Screen.PaymentHistory.route) {
            val viewModel: PaymentViewModel = hiltViewModel()
            val uiState by viewModel.uiState.collectAsState()
            
            PaymentHistoryScreen(
                uiState = uiState,
                onTransactionClick = { transactionId ->
                    // TODO: Navigate to transaction details
                },
                onNavigateBack = { navController.popBackStack() }
            )
        }
        
        // Chat with deep link
        composable(
            route = Screen.Chat.route,
            arguments = listOf(
                navArgument("rideId") { type = NavType.StringType }
            ),
            deepLinks = listOf(
                navDeepLink { uriPattern = Screen.DEEP_LINK_CHAT }
            )
        ) { backStackEntry ->
            val rideId = backStackEntry.arguments?.getString("rideId") ?: ""
            val viewModel: ChatViewModel = hiltViewModel()
            val profileViewModel: ProfileViewModel = hiltViewModel()
            val profile by profileViewModel.profile.collectAsState()
            
            ChatScreen(
                rideId = rideId,
                currentUserId = profile?.id ?: "",
                otherUserName = "Driver", // TODO: Get actual driver name
                onBackClick = { navController.popBackStack() },
                viewModel = viewModel
            )
        }
        
        // Profile and settings
        composable(Screen.Profile.route) {
            val viewModel: ProfileViewModel = hiltViewModel()
            ProfileScreen(
                viewModel = viewModel,
                onNavigateToEmergencyContacts = {
                    navController.navigate(Screen.EmergencyContacts.route)
                },
                onNavigateToVehicleDetails = {
                    // Not applicable for rider app
                },
                isDriver = false
            )
        }
        
        composable(Screen.EmergencyContacts.route) {
            val viewModel: ProfileViewModel = hiltViewModel()
            EmergencyContactsScreen(
                viewModel = viewModel,
                onNavigateBack = { navController.popBackStack() }
            )
        }
        
        composable(Screen.Settings.route) {
            val viewModel: SettingsViewModel = hiltViewModel()
            SettingsScreen(
                viewModel = viewModel,
                onLogout = {
                    navController.navigate(Screen.Login.route) {
                        popUpTo(0) { inclusive = true }
                    }
                },
                isDriverApp = false
            )
        }
        
        composable(Screen.NotificationPreferences.route) {
            val viewModel: SettingsViewModel = hiltViewModel()
            val settings by viewModel.settings.collectAsState()
            
            NotificationPreferencesScreen(
                preferences = settings.notificationPreferences,
                onPreferenceChanged = { type, enabled ->
                    viewModel.updateNotificationPreference(type, enabled)
                },
                onResetToDefaults = {
                    viewModel.resetNotificationPreferences()
                },
                onNavigateBack = { navController.popBackStack() }
            )
        }
        
        composable(Screen.RatingHistory.route) {
            val viewModel: RatingViewModel = hiltViewModel()
            val uiState by viewModel.uiState.collectAsState()
            
            RatingHistoryScreen(
                uiState = uiState,
                onNavigateBack = { navController.popBackStack() }
            )
        }
    }
}
