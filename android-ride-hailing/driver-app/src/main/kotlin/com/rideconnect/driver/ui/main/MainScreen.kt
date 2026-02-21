package com.rideconnect.driver.ui.main

import androidx.compose.foundation.layout.padding
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.ui.Modifier
import androidx.navigation.NavHostController
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import com.rideconnect.core.common.navigation.Screen
import com.rideconnect.core.common.ui.ProfileScreen
import com.rideconnect.core.common.ui.RideHistoryScreen
import com.rideconnect.driver.ui.earnings.EarningsScreen
import com.rideconnect.driver.ui.home.DriverHomeScreen
import com.rideconnect.driver.ui.navigation.DriverDrawerContent
import com.rideconnect.driver.ui.ratings.DriverRatingsScreen
import com.rideconnect.driver.ui.settings.DriverSettingsScreen
import kotlinx.coroutines.launch

/**
 * Main screen wrapper for the Driver App that includes drawer navigation.
 * This screen manages the navigation drawer with Home, Earnings, Ratings, History, Profile, and Settings.
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun MainScreen(
    mainNavController: NavHostController,
    modifier: Modifier = Modifier
) {
    val drawerNavController = rememberNavController()
    val drawerState = rememberDrawerState(initialValue = DrawerValue.Closed)
    val scope = rememberCoroutineScope()
    
    ModalNavigationDrawer(
        drawerState = drawerState,
        drawerContent = {
            DriverDrawerContent(
                navController = drawerNavController,
                drawerState = drawerState
            )
        },
        modifier = modifier
    ) {
        NavHost(
            navController = drawerNavController,
            startDestination = Screen.DriverHome.route
        ) {
            // Home screen
            composable(Screen.DriverHome.route) {
                DriverHomeScreen(
                    onNavigateToActiveRide = { rideId ->
                        mainNavController.navigate(Screen.ActiveRide.createRoute(rideId))
                    },
                    onOpenDrawer = {
                        scope.launch {
                            drawerState.open()
                        }
                    }
                )
            }
            
            // Earnings screen
            composable(Screen.Earnings.route) {
                EarningsScreen(
                    onNavigateToRideReceipt = { rideId ->
                        mainNavController.navigate(Screen.RideReceipt.createRoute(rideId))
                    },
                    onOpenDrawer = {
                        scope.launch {
                            drawerState.open()
                        }
                    }
                )
            }
            
            // Ratings screen
            composable(Screen.DriverRatings.route) {
                DriverRatingsScreen(
                    onOpenDrawer = {
                        scope.launch {
                            drawerState.open()
                        }
                    }
                )
            }
            
            // Ride history screen
            composable(Screen.RideHistory.route) {
                RideHistoryScreen(
                    onNavigateToReceipt = { rideId ->
                        mainNavController.navigate(Screen.RideReceipt.createRoute(rideId))
                    },
                    onNavigateBack = { /* Handled by drawer */ }
                )
            }
            
            // Profile screen
            composable(Screen.Profile.route) {
                ProfileScreen(
                    onNavigateToEmergencyContacts = {
                        mainNavController.navigate(Screen.EmergencyContacts.route)
                    },
                    onNavigateBack = { /* Handled by drawer */ }
                )
            }
            
            // Settings screen
            composable(Screen.DriverSettings.route) {
                DriverSettingsScreen(
                    onNavigateToNotificationPreferences = {
                        mainNavController.navigate(Screen.NotificationPreferences.route)
                    },
                    onNavigateToLogin = {
                        mainNavController.navigate(Screen.Login.route) {
                            popUpTo(0) { inclusive = true }
                        }
                    },
                    onOpenDrawer = {
                        scope.launch {
                            drawerState.open()
                        }
                    }
                )
            }
        }
    }
}
