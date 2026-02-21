package com.rideconnect.driver.navigation

import androidx.compose.runtime.Composable
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
import com.rideconnect.driver.ui.auth.LoginScreen
import com.rideconnect.driver.ui.auth.OtpVerificationScreen
import com.rideconnect.driver.ui.main.MainScreen
import com.rideconnect.driver.ui.ride.ActiveRideScreen

/**
 * Navigation graph for the Driver App.
 * Defines all navigation routes, arguments, and deep links.
 */
@Composable
fun DriverNavGraph(
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
            LoginScreen(
                onNavigateToOtpVerification = { phoneNumber ->
                    navController.navigate(Screen.OtpVerification.createRoute(phoneNumber))
                },
                onLoginSuccess = {
                    navController.navigate(Screen.DriverHome.route) {
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
            val phoneNumber = backStackEntry.arguments?.getString("phoneNumber") ?: ""
            OtpVerificationScreen(
                phoneNumber = phoneNumber,
                onNavigateBack = { navController.popBackStack() },
                onVerificationSuccess = {
                    navController.navigate(Screen.DriverHome.route) {
                        popUpTo(Screen.Login.route) { inclusive = true }
                    }
                }
            )
        }
        
        // Driver home screen with drawer navigation
        composable(Screen.DriverHome.route) {
            MainScreen(mainNavController = navController)
        }
        
        // Active ride with deep link
        composable(
            route = Screen.ActiveRide.route,
            arguments = listOf(
                navArgument("rideId") { type = NavType.StringType }
            ),
            deepLinks = listOf(
                navDeepLink { uriPattern = Screen.DEEP_LINK_ACTIVE_RIDE }
            )
        ) { backStackEntry ->
            val rideId = backStackEntry.arguments?.getString("rideId") ?: ""
            val viewModel: DriverViewModel = hiltViewModel()
            ActiveRideScreen(
                rideId = rideId,
                viewModel = viewModel,
                onNavigateToChat = {
                    navController.navigate(Screen.Chat.createRoute(rideId))
                },
                onNavigateToHome = {
                    navController.navigate(Screen.DriverHome.route) {
                        popUpTo(Screen.DriverHome.route) { inclusive = true }
                    }
                },
                onNavigateBack = { navController.popBackStack() }
            )
        }
        
        // Earnings screen
        composable(Screen.Earnings.route) {
            EarningsScreen(
                onNavigateToRideReceipt = { rideId ->
                    navController.navigate(Screen.RideReceipt.createRoute(rideId))
                },
                onOpenDrawer = { /* TODO: Open drawer */ }
            )
        }
        
        // Ratings screen
        composable(Screen.DriverRatings.route) {
            val viewModel: RatingViewModel = hiltViewModel()
            val uiState by viewModel.uiState.collectAsState()
            DriverRatingsScreen(
                uiState = uiState,
                acceptanceRate = 85.0, // TODO: Get from driver stats
                cancellationRate = 3.5, // TODO: Get from driver stats
                completionRate = 97.0, // TODO: Get from driver stats
                onOpenDrawer = { /* TODO: Open drawer */ }
            )
        }
        
        // Driver settings
        composable(Screen.DriverSettings.route) {
            val viewModel: DriverViewModel = hiltViewModel()
            DriverSettingsScreen(
                viewModel = viewModel,
                onNavigateToNotificationPreferences = {
                    navController.navigate(Screen.NotificationPreferences.route)
                },
                onNavigateToLogin = {
                    navController.navigate(Screen.Login.route) {
                        popUpTo(0) { inclusive = true }
                    }
                },
                onOpenDrawer = { /* TODO: Open drawer */ }
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
                onDateRangeSelected = { startDate, endDate ->
                    // TODO: Implement date range filter
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
            val ride by viewModel.currentRide.collectAsState()
            
            ride?.let { rideData ->
                RideReceiptScreen(
                    ride = rideData,
                    driverName = rideData.driverName,
                    driverPhone = rideData.driverPhone,
                    onShareClick = {
                        // TODO: Implement share functionality
                    },
                    onBackClick = { navController.popBackStack() }
                )
            }
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
            val currentUserId = "driver_id" // TODO: Get from auth state
            val otherUserName = "Rider" // TODO: Get from ride data
            ChatScreen(
                rideId = rideId,
                currentUserId = currentUserId,
                otherUserName = otherUserName,
                onBackClick = { navController.popBackStack() },
                viewModel = viewModel
            )
        }
        
        // Profile and settings
        composable(Screen.Profile.route) {
            ProfileScreen(
                onNavigateToEmergencyContacts = {
                    navController.navigate(Screen.EmergencyContacts.route)
                },
                onNavigateToVehicleDetails = {
                    // TODO: Navigate to vehicle details
                },
                isDriver = true
            )
        }
        
        composable(Screen.EmergencyContacts.route) {
            EmergencyContactsScreen(
                onNavigateBack = { navController.popBackStack() }
            )
        }
        
        composable(Screen.NotificationPreferences.route) {
            val preferences = mapOf(
                NotificationType.RIDE_REQUEST to true,
                NotificationType.RIDE_ACCEPTED to true,
                NotificationType.RIDE_STARTED to true,
                NotificationType.RIDE_COMPLETED to true,
                NotificationType.RIDE_CANCELLED to true,
                NotificationType.NEW_MESSAGE to true,
                NotificationType.SCHEDULED_RIDE_REMINDER to true,
                NotificationType.PROMOTION to false,
                NotificationType.GENERAL to true
            )
            NotificationPreferencesScreen(
                preferences = preferences,
                onPreferenceChanged = { type, enabled ->
                    // TODO: Save preference
                },
                onResetToDefaults = {
                    // TODO: Reset to defaults
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
