package com.rideconnect.rider.navigation

import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.navigation.NavHostController
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import com.rideconnect.core.common.navigation.Screen
import com.rideconnect.core.domain.viewmodel.AuthState
import com.rideconnect.core.domain.viewmodel.AuthViewModel
import com.rideconnect.rider.ui.auth.LoginScreen
import com.rideconnect.rider.ui.auth.OtpVerificationScreen
import com.rideconnect.rider.ui.home.HomeScreen

@Composable
fun RiderNavGraph(
    navController: NavHostController = rememberNavController(),
    authViewModel: AuthViewModel = hiltViewModel()
) {
    val authState by authViewModel.authState.collectAsStateWithLifecycle()
    
    // Determine start destination based on auth state
    val startDestination = when (authState) {
        is AuthState.Authenticated -> Screen.RiderHome.route
        else -> Screen.Login.route
    }
    
    NavHost(
        navController = navController,
        startDestination = startDestination
    ) {
        composable(Screen.Login.route) {
            LoginScreen(
                onNavigateToOtpVerification = {
                    navController.navigate(Screen.OtpVerification.route) {
                        // Don't allow going back to login after OTP is sent
                        popUpTo(Screen.Login.route) { inclusive = false }
                    }
                },
                onLoginSuccess = {
                    navController.navigate(Screen.RiderHome.route) {
                        // Clear back stack when login is successful
                        popUpTo(Screen.Login.route) { inclusive = true }
                    }
                }
            )
        }
        
        composable(Screen.OtpVerification.route) {
            OtpVerificationScreen(
                onNavigateBack = {
                    navController.popBackStack()
                },
                onVerificationSuccess = {
                    navController.navigate(Screen.RiderHome.route) {
                        // Clear back stack when verification is successful
                        popUpTo(Screen.Login.route) { inclusive = true }
                    }
                }
            )
        }
        
        composable(Screen.RiderHome.route) {
            HomeScreen(
                onNavigateToRideRequest = {
                    navController.navigate(Screen.RideRequest.route)
                },
                onNavigateToScheduleRide = {
                    navController.navigate(Screen.ScheduleRide.route)
                },
                onNavigateToParcelDelivery = {
                    navController.navigate(Screen.ParcelDelivery.route)
                },
                onNavigateToRideTracking = { rideId ->
                    navController.navigate(Screen.RideTracking.createRoute(rideId))
                },
                onNavigateToSettings = {
                    navController.navigate(Screen.Settings.route)
                }
            )
        }
    }
}
