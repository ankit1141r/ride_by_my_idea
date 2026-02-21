package com.rideconnect.rider.ui.main

import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Scaffold
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.navigation.NavHostController
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import com.rideconnect.core.common.navigation.Screen
import com.rideconnect.core.common.ui.ProfileScreen
import com.rideconnect.core.common.ui.RideHistoryScreen
import com.rideconnect.rider.ui.home.HomeScreen
import com.rideconnect.rider.ui.navigation.RiderBottomNavigation

/**
 * Main screen wrapper for the Rider App that includes bottom navigation.
 * This screen manages the bottom navigation tabs: Home, History, and Profile.
 */
@Composable
fun MainScreen(
    mainNavController: NavHostController,
    modifier: Modifier = Modifier
) {
    val bottomNavController = rememberNavController()
    
    Scaffold(
        bottomBar = {
            RiderBottomNavigation(navController = bottomNavController)
        },
        modifier = modifier
    ) { paddingValues ->
        NavHost(
            navController = bottomNavController,
            startDestination = Screen.RiderHome.route,
            modifier = Modifier.padding(paddingValues)
        ) {
            // Home tab
            composable(Screen.RiderHome.route) {
                HomeScreen(
                    onNavigateToRideRequest = {
                        mainNavController.navigate(Screen.RideRequest.route)
                    },
                    onNavigateToScheduleRide = {
                        mainNavController.navigate(Screen.ScheduleRide.route)
                    },
                    onNavigateToParcelDelivery = {
                        mainNavController.navigate(Screen.ParcelDelivery.route)
                    },
                    onNavigateToRideTracking = { rideId ->
                        mainNavController.navigate(Screen.RideTracking.createRoute(rideId))
                    },
                    onNavigateToSettings = {
                        mainNavController.navigate(Screen.Settings.route)
                    }
                )
            }
            
            // History tab
            composable(Screen.RideHistory.route) {
                RideHistoryScreen(
                    onNavigateToReceipt = { rideId ->
                        mainNavController.navigate(Screen.RideReceipt.createRoute(rideId))
                    },
                    onNavigateBack = { /* No back action needed for bottom nav */ }
                )
            }
            
            // Profile tab
            composable(Screen.Profile.route) {
                ProfileScreen(
                    onNavigateToEmergencyContacts = {
                        mainNavController.navigate(Screen.EmergencyContacts.route)
                    },
                    onNavigateBack = { /* No back action needed for bottom nav */ }
                )
            }
        }
    }
}
